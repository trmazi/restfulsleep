from flask_restful import Resource
from api.precheck import RequestPreCheck

from api.data.endpoints.news import NewsData

class getAllNews(Resource):
    def get(self):
        sessionState, session = RequestPreCheck.getSession()
        if not sessionState:
            return session
        
        data = NewsData.getAllNews()
        return data, 200

class getNews(Resource):
    def get(self, newsId):
        sessionState, session = RequestPreCheck.getSession()
        if not sessionState:
            return session
        
        data = NewsData.getNews(newsId)
        return {
            'status': 'success',
            'news': data
        }, 200 