from flask_restful import Resource, reqparse

from api.data.mysql import MySQLBase

class userFromPIN(Resource):
    def get(self):
        data = MySQLBase.pull('user')

        parser = reqparse.RequestParser()
        parser.add_argument('username', type=str)
        parser.add_argument('pin', type=str)

        args = parser.parse_args()
        username = str(args['username'])
        pin = str(args['pin'])

        for user in data:
            if username == user[2] and pin == user[1]:
                return {'user': 
                    {
                        'id':str(user[0]),
                        'name':user[2],
                        'pin':user[1],
                        'email':user[4],
                        'is_admin':str(user[5])
                    }
                }, 200
        
        # Unknown user. sucks to suck :shrug:
        return {'status': '0'}, 204