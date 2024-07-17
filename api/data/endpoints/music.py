from api.data.mysql import MySQLBase
from api.data.types import Music, Attempt, Score
from api.data.json import JsonEncoded

class MusicData:
    @staticmethod
    def getAllMusic(game: str = None, version: int = None, limit: int = None, chart: int = None, song_ids: list[int] = None) -> list[dict]:
        with MySQLBase.SessionLocal() as session:
            # Get the list of songs for a game or version
            print(song_ids)
            musicQuery = (
                session.query(Music)
                .filter(Music.game == game, Music.version == version, Music.songid.in_(song_ids) if song_ids else True, Music.chart == chart if chart else True)
                .order_by(Music.songid.desc())
            )
            result = musicQuery.all()

        musicData = []
        for song in result:
            musicData.append({
                'id': song.songid,
                'chart': song.chart,
                'name': song.name,
                'artist': song.artist,
                'genre': song.genre,
                'data': JsonEncoded.deserialize(song.data)
            })
            
        return musicData