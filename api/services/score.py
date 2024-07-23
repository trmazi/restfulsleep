from flask_restful import Resource
from flask import request

from api.constants import APIConstants
from api.data.endpoints.score import ScoreData

class Records(Resource):
    def get(self):
        data = ScoreData.getAllRecords(game = 'ddr', version = 11)
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