from api.constants import ValidatedDict
from api.data.json import JsonEncoded
from api.data.mysql import MySQLBase
from api.data.types import Arcade, ArcadeOwner, ArcadeSettings
from api.data.data import BaseData
from api.data.endpoints.user import UserData

class ArcadeData:   
    def getArcade(arcadeId: int) -> ValidatedDict | None:
        with MySQLBase.SessionLocal() as session:
            arcade = session.query(Arcade).filter(Arcade.id == arcadeId).first()
            if arcade is None:
                return None
            else:
                return ValidatedDict({
                    'id': int(arcade.id),
                    'name': arcade.name,
                    'description': arcade.description,
                    'pin': int(arcade.pin),
                    'data': JsonEncoded.deserialize(arcade.data)
                })
            
    def getAllArcades() -> list[ValidatedDict]:
        with MySQLBase.SessionLocal() as session:
            arcades = session.query(Arcade).filter().all()
            if arcades is None:
                return None
            else:
                formattedArcades = []
                for arcade in arcades:
                    owners = ArcadeData.getArcadeOwners(arcade.id)
                    for index, owner in enumerate(owners):
                        owners[index] = UserData.getUsername(owner)

                    formattedArcade = {
                        'id': int(arcade.id),
                        'name': arcade.name,
                        'description': arcade.description,
                        'owners': owners,
                        'data': JsonEncoded.deserialize(arcade.data)
                    }
                    formattedArcades.append(ValidatedDict(formattedArcade))
                return formattedArcades

    def putArcade(arcadeId: int = None, newArcade: dict = None) -> ValidatedDict | None:
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

            return ValidatedDict({
                'id': int(arcade.id),
                'name': arcade.name,
                'description': arcade.description,
                'pin': int(arcade.pin),
                'data': JsonEncoded.deserialize(arcade.data)
            })
        
    def updateArcadeNameDesc(arcadeId: int, new_name: str, new_desc: str, beta: bool) -> str | None:
        arcade = ArcadeData.getArcade(arcadeId)
        if not arcade:
            return 'No arcade found!'

        with MySQLBase.SessionLocal() as session:
            arcade = session.query(Arcade).filter(Arcade.id == arcadeId).first()
            if arcade:            
                arcade.name = str(new_name)
                arcade.description = str(new_desc)

                data = JsonEncoded.deserialize(arcade.data)
                data['is_beta'] = beta
                arcade.data = JsonEncoded.serialize(data)
                session.commit()
                
            return None
        
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
        
    def getArcadeSettings(arcadeId: int, game: str, version: int, type: str) -> ValidatedDict | None:
        with MySQLBase.SessionLocal() as session:
            arcadeSettings = session.query(ArcadeSettings).filter(ArcadeSettings.arcadeid == arcadeId, ArcadeSettings.game == game, ArcadeSettings.version == version, ArcadeSettings.type == type).first()
            if arcadeSettings is None:
                return None
            else:
                return ValidatedDict(JsonEncoded.deserialize(arcadeSettings.data))
            
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

    def fromName(arcadeName: str) -> ValidatedDict | None:
        with MySQLBase.SessionLocal() as session:
            arcade = session.query(Arcade).filter(Arcade.name == arcadeName).first()
            if arcade is None:
                return None
            else:
                return ValidatedDict({
                    'id': int(arcade.id),
                    'name': arcade.name,
                    'description': arcade.description,
                    'pin': int(arcade.pin),
                    'data': JsonEncoded.deserialize(arcade.data)
                })
            
    def getArcadeName(arcadeId: int) -> str | None:
        with MySQLBase.SessionLocal() as session:
            arcade = session.query(Arcade.name).filter(Arcade.id == arcadeId).first()
            return arcade.name
        
    def getArcadeOwners(arcadeId: int) -> list[int]:
        with MySQLBase.SessionLocal() as session:
            arcades = session.query(ArcadeOwner).filter(ArcadeOwner.arcadeid == arcadeId).all()
            if arcades is None:
                return None
            
            return [arcade.userid for arcade in arcades]
        
    def putArcadeOwner(arcadeId: int, userId: int) -> bool:
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
        
    def removeArcadeOwner(arcadeId: int, userId: int) -> bool:
        with MySQLBase.SessionLocal() as session:
            try:
                arcade = session.query(ArcadeOwner).filter_by(userid=userId, arcadeid=arcadeId).first()
                if arcade is None:
                    return False

                session.delete(arcade)
                session.commit()
                return True
            except Exception as e:
                session.rollback()
                return False

    def getUserArcades(userId: int) -> list[int]:
        with MySQLBase.SessionLocal() as session:
            arcades = session.query(ArcadeOwner).filter(ArcadeOwner.userid == userId).all()
            if arcades is None:
                return None
            else:
                return [arcade.arcadeid for arcade in arcades]
            
    def checkOwnership(userId: int, arcadeId: int) -> bool:
        user = UserData.getUser(userId)
        if user.get_bool('admin'):
            return True

        with MySQLBase.SessionLocal() as session:
            arcade = session.query(ArcadeOwner).filter(ArcadeOwner.userid == userId, ArcadeOwner.arcadeid == arcadeId).first()
            if arcade is None:
                return False
            else:
                return True