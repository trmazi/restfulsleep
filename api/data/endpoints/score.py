from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict
from api.data.mysql import MySQLBase
from api.data.types import Music, Attempt, Score
from api.data.json import JsonEncoded

from api.data.endpoints.music import MusicData
from api.data.endpoints.profiles import ProfileData

class ScoreData:
    @staticmethod
    def getAllRecords(game: str = None, version: int = None, userId: int = None, machineId: int = None, limit: int = 1) -> dict:
        with MySQLBase.SessionLocal() as session:
            # Get the list of songs matching the game and version
            musicQuery = (
                session.query(Music)
                .filter(Music.game == game)
                .order_by(Music.songid.desc())
            )
            musicData = musicQuery.all()

            scores = []
            music_ids = [song.id for song in musicData]

            # If there are no songs matching, return an empty list
            if not music_ids:
                return scores

            # Get attempts for the retrieved songs in one query
            attemptQuery = session.query(Score).filter(Score.musicid.in_(music_ids))

            if userId is not None:
                attemptQuery = attemptQuery.filter(Score.userid == userId)

            if machineId is not None:
                attemptQuery = attemptQuery.filter(Score.lid == machineId)

            attemptQuery = attemptQuery.order_by(Score.musicid, Score.timestamp.desc()).all()

            # Group attempts by music id and limit the number of attempts per song
            attempts_by_music_id = {}
            for attempt in attemptQuery:
                if attempt.musicid not in attempts_by_music_id:
                    attempts_by_music_id[attempt.musicid] = []
                if len(attempts_by_music_id[attempt.musicid]) < limit:
                    attempts_by_music_id[attempt.musicid].append(attempt)

            # Transform the results into the desired format
            songs = []
            for song in musicData:
                songData = {
                    'title': song.name,
                    'artist': song.artist,
                    'genre': song.genre,
                    'chart': song.chart,
                    'data': JsonEncoded.deserialize(song.data),
                    'scores': []
                }
                song_attempts = attempts_by_music_id.get(song.id, [])
                for result in song_attempts:
                    data = JsonEncoded.deserialize(result.data)
                    songData['scores'].append(
                        {
                            'timestamp': result.timestamp,
                            'userId': result.userid,
                            'musicId': result.musicid,
                            'machineId': result.lid,
                            'points': result.points,
                            'combos': data.get('combo'),
                            'halo': data.get('halo'),
                        }
                    )

                songs.append(songData)

            return songs
        
    @staticmethod
    def getAllAttempts(game: str, version: int = None, userId: int = None, machineId: int = None) -> List[Dict]:
        allMusic = MusicData.getAllMusic(game, version)
        db_ids = [music['db_id'] for music in allMusic]
        music_dict = {music['db_id']: music for music in allMusic}

        def fetch_attempts(batch_db_ids):
            with MySQLBase.SessionLocal() as session:
                query = (
                    session.query(Attempt)
                    .filter(Attempt.musicid.in_(batch_db_ids))
                    .order_by(Attempt.timestamp.desc())
                )

                if userId is not None:
                    query = query.filter(Attempt.userid == userId)
                if machineId is not None:
                    query = query.filter(Attempt.lid == machineId)

                results = query.limit(100).all()
                attempts = []
                for attempt in results:
                    attemptUser = ProfileData.getProfile(game, version, attempt.userid, True)
                    if attemptUser == None:
                        continue

                    attempts.append({
                        'song': music_dict.get(attempt.musicid, {}),
                        'timestamp': attempt.timestamp,
                        'userId': attempt.userid,
                        'username': attemptUser.get('username', ''),
                        'musicId': attempt.musicid,
                        'machineId': attempt.lid,
                        'points': attempt.points,
                        'newRecord': bool(attempt.new_record),
                        'data': JsonEncoded.deserialize(attempt.data),
                    })

                return attempts

        # Split db_ids into chunks
        batch_size = len(db_ids) // 8 + 1
        db_id_batches = [db_ids[i:i + batch_size] for i in range(0, len(db_ids), batch_size)]

        attempts = []
        
        with ThreadPoolExecutor(max_workers=8) as executor:
            futures = [executor.submit(fetch_attempts, batch) for batch in db_id_batches]
            for future in as_completed(futures):
                attempts.extend(future.result())

        # Sort results by timestamp (newest first)
        attempts.sort(key=lambda x: x['timestamp'], reverse=True)
        
        return attempts
    
    @staticmethod
    def getAttempts(game: str, songId: int, userId: int = None) -> List[Dict]:
        with MySQLBase.SessionLocal() as session:
            query = (
                session.query(Attempt)
                .filter(Attempt.musicid == songId)
                .order_by(Attempt.timestamp.desc())
            )

            if userId is not None:
                query = query.filter(Attempt.userid == userId)

            results = query.limit(100).all()
        attempts = []
        for attempt in results:
            attemptUser = ProfileData.getProfile(game, None, attempt.userid, True)
            if attemptUser == None:
                continue

            attempts.append({
                'timestamp': attempt.timestamp,
                'userId': attempt.userid,
                'username': attemptUser.get('username', ''),
                'musicId': attempt.musicid,
                'machineId': attempt.lid,
                'points': attempt.points,
                'newRecord': bool(attempt.new_record),
                'data': JsonEncoded.deserialize(attempt.data),
            })

        return attempts
    
    @staticmethod
    def getRecords(game: str, songId: int, userId: int = None) -> List[Dict]:
        with MySQLBase.SessionLocal() as session:
            query = (
                session.query(Score)
                .filter(Score.musicid == songId)
                .order_by(Score.points.desc())
            )

            if userId is not None:
                query = query.filter(Score.userid == userId)

            results = query.limit(100).all()
        records = []
        for record in results:
            recordUser = ProfileData.getProfile(game, None, record.userid, True)
            if recordUser == None:
                continue

            records.append({
                'timestamp': record.timestamp,
                'userId': record.userid,
                'username': recordUser.get('username', ''),
                'musicId': record.musicid,
                'machineId': record.lid,
                'points': record.points,
                'data': JsonEncoded.deserialize(record.data),
            })

        return records

    @staticmethod
    def transferUserRecords(game: str, fromUserId: int, toUserId: int):
        """
        Transfers all records and attempts from one userId to another.
        """
        with MySQLBase.SessionLocal() as session:
            musicQuery = (
                session.query(Music)
                .filter(Music.game == game)
                .order_by(Music.songid.desc())
            )
            musicData = musicQuery.all()
            music_ids = [song.id for song in musicData]

            duplicate_scores = (
                session.query(Score.musicid)
                .filter(Score.userid == toUserId, Score.musicid.in_(music_ids))
            ).subquery()

            scores_to_transfer = (
                session.query(Score)
                .filter(
                    Score.userid == fromUserId,
                    Score.musicid.in_(music_ids),
                    ~Score.musicid.in_(session.query(duplicate_scores.c.musicid)),
                )
            ).all()

            for score in scores_to_transfer:
                score.userid = toUserId
                session.add(score)

            (
                session.query(Attempt)
                .filter(Attempt.userid == fromUserId, Attempt.musicid.in_(music_ids))
                .update({Attempt.userid: toUserId}, synchronize_session=False)
            )
            
            session.commit()

        return len(scores_to_transfer)
    
    @staticmethod
    def getUserStats(userId: int):
        with MySQLBase.SessionLocal() as session:
            attempt_results = (
                session.query(
                    Attempt.timestamp,
                    Attempt.musicid,
                    Attempt.lid,
                    Attempt.points,
                    Attempt.new_record
                )
                .filter(Attempt.userid == userId)
                .all()
            )

            record_results = (
                session.query(
                    Score.timestamp,
                    Score.musicid,
                    Score.lid,
                    Score.points
                )
                .filter(Score.userid == userId)
                .all()
            )

        attempts = [{
            'timestamp': a.timestamp,
            'musicId': a.musicid,
            'machineId': a.lid,
            'points': a.points,
            'newRecord': bool(a.new_record),
        } for a in attempt_results]

        records = [{
            'timestamp': r.timestamp,
            'musicId': r.musicid,
            'machineId': r.lid,
            'points': r.points,
        } for r in record_results]

        return {'attempts': attempts, 'records': records}
    