from api.data.json import JsonEncoded
from api.data.mysql import MySQLBase
from api.data.types import Arcade, ArcadeOwner

class ArcadeData:   
    def getArcade(arcadeId: int):
        with MySQLBase.SessionLocal() as session:
            arcade = session.query(Arcade).filter(Arcade.id == arcadeId).first()
            if arcade is None:
                return None
            else:
                return {
                    'id': int(arcade.id),
                    'name': arcade.name,
                    'description': arcade.description,
                    'pin': int(arcade.pin),
                    'data': JsonEncoded.deserialize(arcade.data)
                }
            
    def getArcadeName(arcadeId: int):
        with MySQLBase.SessionLocal() as session:
            arcade = session.query(Arcade.name).filter(Arcade.id == arcadeId).first()
            return arcade.name
        
    def getArcadeOwners(arcadeId: int):
        with MySQLBase.SessionLocal() as session:
            arcades = session.query(ArcadeOwner).filter(ArcadeOwner.arcadeid == arcadeId).all()
            if arcades is None:
                return None
            
            return [arcade.userid for arcade in arcades]

    def getUserArcades(userId: int) -> dict:
        with MySQLBase.SessionLocal() as session:
            arcades = session.query(ArcadeOwner).filter(ArcadeOwner.userid == userId).all()
            if arcades is None:
                return None
            else:
                return [arcade.arcadeid for arcade in arcades]
            
    def checkOwnership(userId: int, arcadeId: int) -> dict:
        with MySQLBase.SessionLocal() as session:
            arcade = session.query(ArcadeOwner).filter(ArcadeOwner.userid == userId, ArcadeOwner.arcadeid == arcadeId).first()
            if arcade is None:
                return False
            else:
                return True