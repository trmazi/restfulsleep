from flask_restful import Resource

from api.data.endpoints.news import NewsData

class getAllNews(Resource):
    def get(self):
        data = NewsData.getAllNews()
        return data, 200

class getNews(Resource):
    def get(self, newsId):
        data = NewsData.getNews(newsId)
        return {
            'news': data
        }, 200