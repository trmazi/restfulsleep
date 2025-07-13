import random
from sqlalchemy import func
from api.constants import ValidatedDict
from api.data.mysql import MySQLBase
from api.data.types import User, Achievement, Arcade, Audit, Card, EditData, Link, Lobby, Machine, Profile, Score, Attempt, Client, News
from api.data.time import Time
from api.data.json import JsonEncoded

class AdminData:
    def getStats() -> ValidatedDict:
        stats = ValidatedDict({})
        with MySQLBase.SessionLocal() as session:
            tables = [User, Achievement, Arcade, Audit, Card, EditData, Link, Lobby, Machine, Profile, Score, Attempt]
            
            for table in tables:
                count = session.query(func.count()).select_from(table).scalar()
                stats[table.__tablename__] = count
        
        return(stats)
    
    def getRecentAuditEvents(limit: int = 10, auditType: str = None) -> list[ValidatedDict]:
        with MySQLBase.SessionLocal() as session:
            auditQuery = session.query(Audit)
            if auditType:
                auditQuery = auditQuery.filter(Audit.type == auditType)

            auditQuery = auditQuery.order_by(Audit.id.desc()).limit(limit).all()
            return [
                ValidatedDict({
                    'id': event.id,
                    'timestamp': event.timestamp,
                    'userid': event.userid,
                    'arcadeid': event.arcadeid,
                    'type': event.type,
                    'data': JsonEncoded.deserialize(event.data)
                })
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

    def getAllClients() -> list[ValidatedDict]:
        with MySQLBase.SessionLocal() as session:
            clientQuery = session.query(Client)
            clientQuery = clientQuery.order_by(Client.id.desc()).all()
            return [
                ValidatedDict({
                    'id': client.id,
                    'timestamp': client.timestamp,
                    'name': client.name,
                    'token': client.token
                })
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
        
    def getAllUsers(noData: bool = False) -> list[ValidatedDict]:
        with MySQLBase.SessionLocal() as session:
            userQuery = session.query(User.id, User.username, User.admin, User.banned, User.data)
            userQuery = userQuery.order_by(User.id.asc()).all()
            return [
                ValidatedDict({
                    'id': user.id,
                    'username': user.username,
                    'admin': bool(user.admin),
                    'banned': bool(user.banned),
                    'data': JsonEncoded.deserialize(user.data) if not noData else None
                })
                for user in userQuery
            ]

    def getAllNews() -> list[ValidatedDict]:
        with MySQLBase.SessionLocal() as session:
            newsQuery = session.query(News)
            newsQuery = newsQuery.order_by(News.id.desc()).all()
            return [
                ValidatedDict({
                    'id': news.id,
                    'timestamp': news.timestamp,
                    'title': news.title,
                    'body': news.body,
                    'data': JsonEncoded.deserialize(news.data)
                })
                for news in newsQuery
            ]
        
    def putNews(title: str = None, body: str = None, data: dict = {}, newsId: int = None) -> bool:
        with MySQLBase.SessionLocal() as session:
            try:
                if newsId is not None:
                    news = session.query(News).filter_by(id=newsId).first()
                    if not news:
                        return False
                else:
                    news = News()
                    news.timestamp = Time.now()
                    session.add(news)

                if title is not None:
                    news.title = title
                if body is not None:
                    news.body = body
                if data is not None:
                    news.data = JsonEncoded.serialize(data)

                session.commit()
                return True

            except Exception as e:
                session.rollback()
                return False
            
    def deleteNews(newsId: int):
        with MySQLBase.SessionLocal() as session:
            try:
                news = session.query(News).filter_by(id=newsId).first()
                if news is None:
                    return False
                
                session.delete(news)
                session.commit()
                return True
            except Exception as e:
                session.rollback()
                return False