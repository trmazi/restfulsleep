from api.data.mysql import MySQLBase
from api.data.types import News
from api.data.json import JsonEncoded

class NewsData:
    def getNews(newsID: int) -> dict:
        with MySQLBase.SessionLocal() as session:
            data = session.query(News).filter(News.id == newsID).first()
            if not data:
                return None
            return {
                'id': data.id,
                'timestamp': data.timestamp,
                'title': data.title,
                'body': data.body,
                'data': JsonEncoded.deserialize(data.data),
            }
        
    def getAllNews(limit: int) -> list[dict]:
        with MySQLBase.SessionLocal() as session:
            data = session.query(News).order_by(News.timestamp.desc()).limit(limit).all()
            if not data:
                return None
            
            posts = []
            for result in data:
                posts.append(
                    {
                        'id': result.id,
                        'timestamp': result.timestamp,
                        'title': result.title,
                        'body': result.body,
                        'data': JsonEncoded.deserialize(result.data),
                    }
                )

            return posts