from flask_restful import Resource

from api.data.endpoints.score import ScoreData

class Records(Resource):
    def get(self):
        data = ScoreData.getAllRecords(game = 'ddr', version = 11)
        return {
            'status': 'success',
            'songs': data
        }, 200
    
class Attempts(Resource):
    def get(self):
        data = ScoreData.getAllRecords(game = 'ddr', version = 18)
        return {
            'status': 'success',
            'songs': data
        }, 200