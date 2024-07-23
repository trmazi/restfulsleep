from api.data.mysql import MySQLBase
from api.data.types import Music, Attempt, Score
from api.data.json import JsonEncoded

class MusicData:
    @staticmethod
    def getAllMusic(game: str = None, version: int = None, limit: int = None, chart: int = None, song_ids: list[int] = None) -> list[dict]:
        with MySQLBase.SessionLocal() as session:
            # Get the list of songs for a game or version
            musicQuery = (
                session.query(Music)
                .filter(Music.game == game, Music.songid.in_(song_ids) if song_ids else True, Music.chart == chart if chart else True)
                .order_by(Music.songid.desc())
            )

            if version is not None:
                musicQuery = musicQuery.filter(Music.version == version)

            result = musicQuery.all()

        # To ensure unique (db_id, chart) pairs
        seen = set()
        musicData = []
        for song in result:
            if (song.id, song.chart) not in seen:
                seen.add((song.id, song.chart))
                musicData.append({
                    'db_id': song.id,
                    'id': song.songid,
                    'chart': song.chart,
                    'name': song.name,
                    'artist': song.artist,
                    'genre': song.genre,
                    'data': JsonEncoded.deserialize(song.data)
                })

        return musicData