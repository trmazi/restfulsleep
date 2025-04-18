import random
from sqlalchemy import func
from api.data.mysql import MySQLBase
from api.data.types import User, Achievement, Arcade, Audit, Card, EditData, Link, Lobby, Machine, Profile, Score, Attempt, Client
from api.data.time import Time
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
    
    def getRecentAuditEvents(limit: int = 10, auditType: str = None) -> list:
        with MySQLBase.SessionLocal() as session:
            auditQuery = session.query(Audit)
            if auditType:
                auditQuery = auditQuery.filter(Audit.type == auditType)

            auditQuery = auditQuery.order_by(Audit.id.desc()).limit(limit).all()
            return [
                {
                    'id': event.id,
                    'timestamp': event.timestamp,
                    'userid': event.userid,
                    'arcadeid': event.arcadeid,
                    'type': event.type,
                    'data': JsonEncoded.deserialize(event.data)
                }
                for event in auditQuery
            ]
    
    def putAuditEvent(auditType: str = None, userid: int = None, arcadeid: int = None, data: dict = {}) -> bool:
        with MySQLBase.SessionLocal() as session:
            newEvent = Audit()
            newEvent.timestamp = Time.now()
            newEvent.type = auditType
            newEvent.userid = userid
            newEvent.arcadeid = arcadeid
            newEvent.data = JsonEncoded.serialize(data)

            session.add(newEvent)
            session.commit()

            return True

    def getAllClients() -> list:
        with MySQLBase.SessionLocal() as session:
            clientQuery = session.query(Client)
            clientQuery = clientQuery.order_by(Client.id.desc()).all()
            return [
                {
                    'id': client.id,
                    'timestamp': client.timestamp,
                    'name': client.name,
                    'token': client.token
                }
                for client in clientQuery
            ]
        
    def putClient(name: str = None) -> bool:
        token = ''.join(random.choice('0123456789ABCDEF') for _ in range(32))

        with MySQLBase.SessionLocal() as session:
            while session.query(Client).filter(Client.token == token).first():
                token = ''.join(random.choice('0123456789ABCDEF') for _ in range(32))

            newClient = Client()
            newClient.timestamp = Time.now()
            newClient.name = name
            newClient.token = token

            session.add(newClient)
            session.commit()

            return True
