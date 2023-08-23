from flask_restful import Resource
from flask import request

class shareServerStatus(Resource):
    def get(self):
        return { "status": 200 }, 200
    
class shareBeginUpload(Resource):
    def post(self):
        print(request.data)
        return { "status": 200 }, 200