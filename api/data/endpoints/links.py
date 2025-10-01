from api.data.mysql import MySQLBase
from api.data.types import Link
from api.data.json import JsonEncoded
from api.constants import ValidatedDict

class LinkData:
    @staticmethod        
    def getAllLinks(game: str, version: int, userId: int) -> list[ValidatedDict] | None:
        '''
        Given the game, version, userId and returns the link data.
        '''
        with MySQLBase.SessionLocal() as session:
            links = session.query(Link).filter(Link.game == game, Link.version == version, Link.userid == userId).all()
            if links:
                linkData = [ValidatedDict({
                    "type": link.type,
                    "otherUserId": link.other_userid,
                    "data": JsonEncoded.deserialize(link.data)
                }) for link in links]
                return linkData
                
            return None
        
    def putLink(game: str, version: int, userId: int, otherUserId: int, type: str) -> bool | None:
        '''
        Given the game, version, userId, rival userId, type and creates the link.
        '''
        with MySQLBase.SessionLocal() as session:
            try:
                link = Link()
                link.game = game
                link.version = version
                link.userid = userId
                link.other_userid = otherUserId
                link.type = type
                link.data = JsonEncoded.serialize(ValidatedDict())
                session.add(link)
                session.commit()
                return True

            except Exception as e:
                session.rollback()
                return False
            
    def deleteLink(game: str, version: int, userId: int, otherUserId: int, type: str):
        with MySQLBase.SessionLocal() as session:
            try:
                link = session.query(Link).filter(Link.game == game, Link.version == version, Link.userid == userId, Link.other_userid == otherUserId, Link.type == type).first()
                if link is None:
                    return False
                
                session.delete(link)
                session.commit()
                return True
            except Exception as e:
                session.rollback()
                return False