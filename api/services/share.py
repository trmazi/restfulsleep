from flask_restful import Resource
from flask import request

class shareServerStatus(Resource):
    def get(self):
        print(request.headers)
        return { "status": "ok" }, 200