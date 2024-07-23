from api.data.mysql import MySQLBase
from api.data.types import Music, Attempt, Score
from api.data.json import JsonEncoded

from api.data.endpoints.music import MusicData

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
    def getAllAttempts(game: str, version: int = None, userId: int = None, machineId: int = None) -> list[dict]:
        allMusic = MusicData.getAllMusic(game, version)
        db_ids = [music['db_id'] for music in allMusic]
        music_dict = {music['db_id']: music for music in allMusic}
        attempts = []

        with MySQLBase.SessionLocal() as session:
            query = (
                session.query(Attempt)
                .filter(Attempt.musicid.in_(db_ids))
                .order_by(Attempt.timestamp.desc())
                .limit(500)
            )

            # Apply additional filters if provided
            if userId is not None:
                query = query.filter(Attempt.userid == userId)
            if machineId is not None:
                query = query.filter(Attempt.lid == machineId)

            # Execute the query and fetch the results
            results = query.all()
            for attempt in results:
                songData = music_dict.get(attempt.musicid, {})
                attempts.append(
                    {
                        'song': songData,
                        'timestamp': attempt.timestamp,
                        'userId': attempt.userid,
                        'musicId': attempt.musicid,
                        'machineId': attempt.lid,
                        'points': attempt.points,
                        'newRecord': bool(attempt.new_record),
                        'data': JsonEncoded.deserialize(attempt.data),
                    }
                )
            
            
        return attempts