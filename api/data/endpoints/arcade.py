from api.data.json import JsonEncoded
from api.data.mysql import MySQLBase
from api.data.types import Arcade, ArcadeOwner, ArcadeSettings
from api.data.data import BaseData

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

    def putArcade(arcadeId: int = None, newArcade: dict = None):
        if newArcade is None:
            return None  # No data provided, return None
        
        # Check required fields
        if 'name' not in newArcade or newArcade['name'] is None:
            raise ValueError("Arcade 'name' is required and cannot be None")
        
        if 'pin' not in newArcade or newArcade['pin'] is None:
            raise ValueError("Arcade 'pin' is required and cannot be None")
        
        with MySQLBase.SessionLocal() as session:
            if arcadeId is not None:
                arcade = session.query(Arcade).filter(Arcade.id == arcadeId).first()
                if arcade is None:
                    return None
            else:
                arcade = Arcade(
                    name = newArcade.get('name'),
                    description = newArcade.get('description'),
                    pin = newArcade.get('pin'),
                    data = JsonEncoded.serialize(newArcade.get('data', {}))
                )
                session.add(arcade)
                session.flush()
            
            arcade.name = newArcade.get('name')
            arcade.description = newArcade.get('description')
            arcade.pin = newArcade.get('pin')
            arcade.data = JsonEncoded.serialize(newArcade.get('data', {}))

            session.commit()

            return {
                'id': int(arcade.id),
                'name': arcade.name,
                'description': arcade.description,
                'pin': int(arcade.pin),
                'data': JsonEncoded.deserialize(arcade.data)
            }
        
    def updateArcadeData(arcadeId: int, new_arcade: dict) -> str | None:
        arcade = ArcadeData.getArcade(arcadeId)
        if not arcade:
            return 'No arcade found!'

        with MySQLBase.SessionLocal() as session:
            arcade = session.query(Arcade).filter(Arcade.id == arcadeId).first()
            if arcade:
                rawData = JsonEncoded.deserialize(arcade.data, True)
                error_code = BaseData.update_data(rawData, new_arcade)
                if error_code:
                    return error_code
            
                arcade.data = JsonEncoded.serialize(rawData)
                session.commit()
                
            return None
        
    def getArcadeSettings(arcadeId: int, game: str, version: int, type: str):
        with MySQLBase.SessionLocal() as session:
            arcadeSettings = session.query(ArcadeSettings).filter(ArcadeSettings.arcadeid == arcadeId, ArcadeSettings.game == game, ArcadeSettings.version == version, ArcadeSettings.type == type).first()
            if arcadeSettings is None:
                return None
            else:
                return JsonEncoded.deserialize(arcadeSettings.data)
            
    def updateArcadeSettings(arcadeId: int, game: str, version: int, type_s: str, new_settings: dict) -> str | None:       
        with MySQLBase.SessionLocal() as session:
            arcadeSettings = session.query(ArcadeSettings).filter(ArcadeSettings.arcadeid == arcadeId, ArcadeSettings.game == game, ArcadeSettings.version == version, ArcadeSettings.type == type_s).first()
            if arcadeSettings:
                rawData = JsonEncoded.deserialize(arcadeSettings.data, True)
                error_code = BaseData.update_data(rawData, new_settings)
                if error_code:
                    return error_code

                arcadeSettings.data = JsonEncoded.serialize(rawData)

            else:
                rawData = JsonEncoded.deserialize("{}", True)
                error_code = BaseData.update_data(rawData, new_settings)
                if error_code:
                    return error_code
                arcadeSettings = ArcadeSettings(
                    arcadeid = arcadeId,
                    game = game,
                    version = version,
                    type = type_s,
                    data = JsonEncoded.serialize(rawData)
                )
                session.add(arcadeSettings)
                session.flush()

            session.commit()
            return None

    def fromName(arcadeName: str):
        with MySQLBase.SessionLocal() as session:
            arcade = session.query(Arcade).filter(Arcade.name == arcadeName).first()
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
        
    def putArcadeOwner(arcadeId: int, userId: int):
        with MySQLBase.SessionLocal() as session:
            try:
                arcade = ArcadeOwner(userid = userId, arcadeid = arcadeId)
                session.add(arcade)
                session.flush()
            except Exception as e:
                session.rollback()
                return False

            session.commit()
            return True

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