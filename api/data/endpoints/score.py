from sqlalchemy import func, and_
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict
from api.data.mysql import MySQLBase
from api.data.types import Music, Attempt, Score
from api.data.json import JsonEncoded
from api.data.cache import LocalCache

from api.data.endpoints.music import MusicData
from api.data.endpoints.profiles import ProfileData

class ScoreData:
    @staticmethod
    def getAllRecords(game: str = None, version: int = None, userId: int = None, machineId: int = None) -> dict:
        musicData = MusicData.getAllSongs(game, version)
        allDBId = [chart['db_id'] for song in musicData for chart in song.get('charts', [])]
        if not allDBId:
            return None

        cacheName = f'web_records_{game}_{version}'
        cacheData = None

        if not userId and not machineId:
            cacheData = LocalCache().getCachedData(cacheName)

        if not cacheData:
            with MySQLBase.SessionLocal() as session:
                subquery = (
                    session.query(
                        Score.musicid,
                        func.max(Score.points).label("max_points")
                    )
                    .filter(Score.musicid.in_(allDBId))
                )

                if userId is not None:
                    subquery = subquery.filter(Score.userid == userId)
                if machineId is not None:
                    subquery = subquery.filter(Score.lid == machineId)
                subquery = subquery.group_by(Score.musicid).subquery()

                bestScores = (
                    session.query(Score)
                    .join(subquery, and_(
                        Score.musicid == subquery.c.musicid,
                        Score.points == subquery.c.max_points
                    ))
                    .order_by(Score.musicid, Score.timestamp.asc())  # earliest timestamp if tie
                    .all()
                )
                bestScoresByDBId = {score.musicid: score for score in bestScores}

            for song in musicData:
                for chart in song.get('charts', []):
                    record = bestScoresByDBId.get(chart['db_id'])
                    if not record:
                        continue

                    recordUser = ProfileData.getProfile(game, version, record.userid, True)
                    if recordUser == None:
                        continue
                    chart['record'] = {
                        'timestamp': record.timestamp,
                        'userId': record.userid,
                        'username': recordUser.get('username', ''),
                        'musicId': record.musicid,
                        'machineId': record.lid,
                        'points': record.points,
                        'data': JsonEncoded.deserialize(record.data),
                    }

            if not userId and not machineId:
                LocalCache().putCachedData(cacheName, musicData)

        return cacheData if cacheData else musicData

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
    