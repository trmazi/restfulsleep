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