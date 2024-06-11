from api.data.json import JsonEncoded
from api.data.mysql import MySQLBase
from api.data.types import GameSettings

class GameData:   
    def getUserGameSettings(userId: int) -> dict:
        with MySQLBase.SessionLocal() as session:
            games = session.query(GameSettings).filter(GameSettings.userid == userId).all()
            if games is None:
                return None
            else:
                return [{
                    'game': game.game,
                    'data': JsonEncoded.deserialize(game.data)
                } for game in games]