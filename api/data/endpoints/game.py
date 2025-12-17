import concurrent.futures
from api.data.json import JsonEncoded
from api.data.mysql import MySQLBase
from api.data.types import GameSettings, Extid, TimeSensitiveSettings
from api.data.time import Time
from api.constants import ValidatedDict

class GameData:   
    def getUserGameSettings(userId: int) -> list[ValidatedDict]:
        with MySQLBase.SessionLocal() as session:
            games = session.query(GameSettings).filter(GameSettings.userid == userId).all()
            if games is None:
                return None
            else:
                return [ValidatedDict({
                    'game': game.game,
                    'data': JsonEncoded.deserialize(game.data)
                }) for game in games]
            
    def getUserGameStats(game: str, userId: int) -> ValidatedDict:
        with MySQLBase.SessionLocal() as session:
            game = session.query(GameSettings.data).filter(
                GameSettings.userid == userId,
                GameSettings.game == game
            ).first()

            if game is None:
                return None
            else:
                return ValidatedDict(JsonEncoded.deserialize(game.data))
            
    def deserialize_game_data(game):
        return game.userid, JsonEncoded.deserialize(game.data)
            
    def getAllGameStats(game: str) -> tuple[int, dict]:
        with MySQLBase.SessionLocal() as session:
            games = session.query(GameSettings.userid, GameSettings.data).filter(
            GameSettings.game == game
        ).all()

        if not games:
            return []

        # Use ThreadPoolExecutor for parallel processing of deserialization
        with concurrent.futures.ThreadPoolExecutor() as executor:
            results = list(executor.map(GameData.deserialize_game_data, games))

        return results
            
    def getUserExtid(game: str, userId: int):
        with MySQLBase.SessionLocal() as session:
            extid = session.query(Extid.extid).filter(Extid.game == game, Extid.userid == userId).first()
            
            if extid is None:
                return None
            else:
                return int(extid.extid)
            
    def getAllExtid(game: str) -> tuple[int, int]:
        with MySQLBase.SessionLocal() as session:
            extIds = session.query(Extid).filter(Extid.game == game).all()
            
            if extIds is None:
                return None
            else:
                return [(int(extId.userid), int(extId.extid)) for extId in extIds]
            
    def getTimeSensitiveSettings(game: str, version: str) -> list[ValidatedDict] | None:
        now = Time.now()

        with MySQLBase.SessionLocal() as session:
            settings = session.query(TimeSensitiveSettings).filter(
                TimeSensitiveSettings.game == game,
                TimeSensitiveSettings.version == version,
                TimeSensitiveSettings.start_time <= now,
                TimeSensitiveSettings.end_time > now,
            ).all()
            
            if settings is None:
                return None
            else:
                return [
                    {
                        "id": setting.name,
                        "start_time": int(setting.start_time),
                        "end_time": int(setting.end_time),
                        "data": ValidatedDict(JsonEncoded.deserialize(setting.data))
                    } for setting in settings
                ]
    
    def getTimeSensitiveSetting(game: str, version: str, name: str):
        now = Time.now()
        
        with MySQLBase.SessionLocal() as session:
            setting = session.query(TimeSensitiveSettings).filter(
                TimeSensitiveSettings.game == game,
                TimeSensitiveSettings.version == version,
                TimeSensitiveSettings.name == name,
                TimeSensitiveSettings.start_time <= now,
                TimeSensitiveSettings.end_time > now,
            ).first()
            
            if setting is None:
                return None
            else:
                return {
                    "id": setting.name,
                    "start_time": int(setting.start_time),
                    "end_time": int(setting.end_time),
                    "data": ValidatedDict(JsonEncoded.deserialize(setting.data))
                }