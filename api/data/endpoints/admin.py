from sqlalchemy import func

from api.data.mysql import MySQLBase
from api.data.types import User, Achievement, Arcade, Audit, Card, EditData, Link, Lobby, Machine, Profile, Score, Attempt
from api.data.json import JsonEncoded

class AdminData:
    def getStats() -> dict:
        stats = {}
        with MySQLBase.SessionLocal() as session:
            tables = [User, Achievement, Arcade, Audit, Card, EditData, Link, Lobby, Machine, Profile, Score, Attempt]
            
            for table in tables:
                count = session.query(func.count()).select_from(table).scalar()
                stats[table.__tablename__] = count
        
        return(stats)
    
    def getRecentAuditEvents(limit: int = 10) -> list:
        with MySQLBase.SessionLocal() as session:
            recent_events = (
                session.query(Audit)
                .order_by(Audit.id.desc())
                .limit(limit)
                .all()
            )
            return [
                {
                    'id': event.id,
                    'timestamp': event.timestamp,
                    'userid': event.userid,
                    'arcadeid': event.arcadeid,
                    'type': event.type,
                    'data': JsonEncoded.deserialize(event.data)
                }
                for event in recent_events
            ]