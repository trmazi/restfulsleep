from typing import Dict, Any
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker

from api.data.json import JsonEncoded
from api.data.types import Refid, Profile, GameSettings

Base = declarative_base()

class MySQLBase:
    engine: Engine = None
    SessionLocal = None

    @staticmethod
    def update_connection(db_config: Dict[str, Any]) -> None:
        user = db_config.get('user', '')
        password = db_config.get('pass', '')
        host = db_config.get('host', 'localhost')
        database = db_config.get('db', '')

        connection_string = f'mysql+mysqlconnector://{user}:{password}@{host}/{database}'
        MySQLBase.engine = create_engine(connection_string)
        MySQLBase.SessionLocal = sessionmaker(bind=MySQLBase.engine)

    def getProfile(game: str, version: int, userId: int, justStats: bool) -> Dict:
        with MySQLBase.SessionLocal() as session:
            refid = session.query(Refid.refid).filter(Refid.userId == userId, Refid.game == game, Refid.version == version).first()
            if not refid:
                return {'status': 'error', 'error_code': 'no profile'}

            profile_data = session.query(Profile.data).filter(Profile.refid == refid[0]).first()
            if not profile_data:
                return {'status': 'error', 'error_code': 'no profile'}

            if justStats:
                stats = session.query(GameSettings.data).filter(GameSettings.game == game, GameSettings.userId == userId).first()
                if stats:
                    data = JsonEncoded.deserialize(stats[0])
            else:
                data = JsonEncoded.deserialize(profile_data[0])

            data['status'] = 'good'
            return data

if MySQLBase.engine:
    Base.metadata.create_all(MySQLBase.engine)