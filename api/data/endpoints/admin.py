from sqlalchemy import func

from api.data.mysql import MySQLBase
from api.data.types import User, Achievement, Arcade, Audit, Card, EditData, Link, Lobby, Machine, Profile, Score, Attempt

class AdminData:
    def getStats() -> dict:
        stats = {}
        with MySQLBase.SessionLocal() as session:
            tables = [User, Achievement, Arcade, Audit, Card, EditData, Link, Lobby, Machine, Profile, Score, Attempt]
            
            for table in tables:
                count = session.query(func.count()).select_from(table).scalar()
                stats[table.__tablename__] = count
        
        return(stats)