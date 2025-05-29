from api.data.mysql import MySQLBase
from api.data.types import Music
from api.data.json import JsonEncoded
from api.data.cache import LocalCache

class MusicData:
    @staticmethod
    def getAllMusic(game: str = None, version: int = None, limit: int = None, chart: int = None, song_ids: list[int] = None) -> list[dict]:
        cacheName = f'music_{game}_{version}'
        musicData = None
        if not song_ids:
            musicData = LocalCache().getCachedData(cacheName)

        if not musicData:
            with MySQLBase.SessionLocal() as session:
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

            if not song_ids:
                LocalCache().putCachedData(cacheName, musicData)

        return musicData
    
    @staticmethod
    def getAllSongs(game: str = None, version: int = None, song_ids: list[int] = None) -> list[dict]:
        cacheName = f'songs_{game}_{version}'
        resultData = None
        if not song_ids:
            resultData = LocalCache().getCachedData(cacheName)

        if not resultData:
            with MySQLBase.SessionLocal() as session:
                musicQuery = (
                    session.query(Music)
                    .filter(Music.game == game, Music.songid.in_(song_ids) if song_ids else True)
                    .order_by(Music.songid.desc(), Music.version.asc())
                )

                if version is not None:
                    musicQuery = musicQuery.filter(Music.version == version)

                result = musicQuery.all()

            seen = set()
            groupedSongs = {}

            for song in result:
                key = (song.id, song.chart)
                if key in seen:
                    continue
                seen.add(key)

                chartData = {
                    'db_id': song.id,
                    'chart': song.chart,
                    'data': JsonEncoded.deserialize(song.data)
                }

                if song.songid not in groupedSongs:
                    category = chartData.get('data', {}).get('category', None)
                    groupedSongs[song.songid] = {
                        'id': song.songid,
                        'name': song.name,
                        'artist': song.artist,
                        'genre': song.genre,
                        'version': category if category else song.version,
                        'charts': []
                    }

                groupedSongs[song.songid]['charts'].append(chartData)

            resultData = list(groupedSongs.values())[0] if len(groupedSongs) == 1 else list(groupedSongs.values())

            if not song_ids:
                LocalCache().putCachedData(cacheName, resultData)

        return resultData
    
    @staticmethod
    def getSongByGameId(game: str, songId: int, version: int = None, chart: int = None) -> list[dict]:
        with MySQLBase.SessionLocal() as session:
            musicQuery = (
                session.query(Music)
                .filter(Music.game == game, Music.songid == songId, Music.chart == chart if chart else True)
                .order_by(Music.songid.desc())
            )

            if version is not None:
                musicQuery = musicQuery.filter(Music.version == version)

            result = musicQuery.all()

        seen = set()
        groupedSongs = {}

        for song in result:
            key = (song.id, song.chart)
            if key in seen:
                continue
            seen.add(key)

            chartData = {
                'db_id': song.id,
                'chart': song.chart,
                'data': JsonEncoded.deserialize(song.data)
            }

            if song.songid not in groupedSongs:
                groupedSongs[song.songid] = {
                    'id': song.songid,
                    'name': song.name,
                    'artist': song.artist,
                    'genre': song.genre,
                    'charts': []
                }

            groupedSongs[song.songid]['charts'].append(chartData)

        return list(groupedSongs.values())[0] if len(groupedSongs) == 1 else list(groupedSongs.values())