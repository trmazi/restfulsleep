from flask_restful import Resource
from flask import request
from api.external.discord import GoodSaniacWebhook

class shareServerStatus(Resource):
    def get(self):
        responseData = {
            "status": 200,
            "message": ""
        }
        return responseData, 200

class shareNewSession(Resource):
    def post(self):
        responseData = {
            "status": 200,
            "message": "",
            "session": "testSession" # Replace with generated Session ID
        }
        return responseData, 200

class shareBeginUpload(Resource):
    def post(self, sessionId, videoId):
        responseData = {
            "status": 200,
            "message": "",
            "url": f'http://10.5.7.3:9090/share/videoUpload/{sessionId}'
        }
        return responseData, 200
    
class shareVideoUpload(Resource):
    def put(self, sessionId):
        if request.data:
            GoodSaniacWebhook().sendVideoMessage(request.data)

        return 200

class shareEndUpload(Resource):
    def post(self, sessionId, videoId):
        responseData = {
            "status": 200,
            "message": ""
        }
        return responseData, 200