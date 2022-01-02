from flask_restful import Resource
from datetime import datetime

from api.data.mysql import MySQLBase

class getAllNews(Resource):
    def get(self):
        data = MySQLBase.pull('news ORDER BY timestamp DESC')
        dicts = []
        for news in data:
            unixtime = news[1]
            humantime = datetime.utcfromtimestamp(unixtime).strftime('%Y-%m-%d')
            v = {'id':news[0],'timestamp':humantime, 'title':news[2], 'body':news[3]}
            dicts.append(v)
        return {
            'news':dicts
        }, 200

class getLatestNews(Resource):
    def get(self):
        data = MySQLBase.pull('news ORDER BY timestamp DESC LIMIT 1')
        dicts = []
        for news in data:
            unixtime = news[1]
            humantime = datetime.utcfromtimestamp(unixtime).strftime('%Y-%m-%d')
            v = {'id':news[0],'timestamp':humantime, 'title':news[2], 'body':news[3]}
            dicts.append(v)
        return {
            'news':dicts
        }, 200