from typing import Dict, Any
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

class MySQLBase:
    engine: Engine = None
    SessionLocal = None

    @staticmethod
    def updateConfig(db_config: Dict[str, Any]) -> None:
        user = db_config.get('user', '')
        password = db_config.get('pass', '')
        host = db_config.get('host', 'localhost')
        database = db_config.get('db', '')

        connection_string = f'mysql+mysqlconnector://{user}:{password}@{host}/{database}'
        MySQLBase.engine = create_engine(
            connection_string,
            pool_pre_ping=True,
            pool_recycle=1800,
            pool_size=10,
            max_overflow=20
        )
        MySQLBase.SessionLocal = sessionmaker(bind=MySQLBase.engine)

if MySQLBase.engine:
    Base.metadata.create_all(MySQLBase.engine)