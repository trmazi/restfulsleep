from flask_restful import Resource
from flask import request

from api.constants import APIConstants
from api.data.endpoints.music import MusicData
from api.data.endpoints.score import ScoreData

class Records(Resource):
    def get(self, game: str):
        version = request.args.get('version')
        if version:
            try:
                version = int(version)
            except:
                version = None

        if not version:
            return APIConstants.bad_end('No version provided!')

        data = ScoreData.getAllRecords(game, version)
        return {
            'status': 'success',
            'songs': data
        }, 200
    
class Attempts(Resource):
    def get(self, game):
        version = request.args.get('version')
        userId = request.args.get('userId')

        if userId:
            try:
                userId = int(userId)
            except:
                userId = None

        if version:
            try:
                version = int(version)
            except:
                version = None

        data = ScoreData.getAllAttempts(game, version, userId)
        return {
            'status': 'success',
            'data': data
        }, 200
    
class TopScore(Resource):
    def get(self, game: str, songId: int):
        songData = MusicData.getSongByGameId(game, songId)
        if not songData:
            return APIConstants.bad_end('Failed to find song!')
        
        for index, chart in enumerate(songData.get('charts')):
            chartRecords = ScoreData.getRecords(game, chart.get('db_id', None))
            songData['charts'][index]['records'] = chartRecords

        return {
            'status': 'success',
            'data': songData
        }, 200