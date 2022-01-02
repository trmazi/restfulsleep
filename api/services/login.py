from flask_restful import Resource, reqparse

from api.data.mysql import MySQLBase

class guidesLoginStatus(Resource):
    def get(self):
        data = MySQLBase.pull('user')

        parser = reqparse.RequestParser()
        parser.add_argument('username', type=str)
        parser.add_argument('pin', type=str)

        args = parser.parse_args()
        username = str(args['username'])
        pin = int(args['pin'])

        print(args)
        print(data)

        for user in data:
            if username == user[2] and pin == user[1]:
                return {'status': '1'}, 200
        
        #User not found.
        return {'status': '0'}, 200