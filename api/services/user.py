from flask_restful import Resource, reqparse
from flask import request

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
        return {'status': '0'}, 205

class userIDFromUsername(Resource):
    def get(self):
        '''
        Get a userID using a user's name.
        '''
        username = request.args.get('username')

        current_error = None
        if username != None:
            userID = MySQLBase.getUserFromName(username)
            if userID == None:
                current_error = 'no_account'
            else:
                return {'user': 
                    {
                        'id':userID,
                    },
                    'status': 'success'
                }, 200
        else:
            current_error = 'no_username'    
        
        # Unknown user. sucks to suck :shrug:
        return {'status': 'error', 'error_code': current_error}

class validateUserPassword(Resource):
    def get(self):
        '''
        Return a bool if it's the correct password.
        '''
        userid = int(request.args.get('id'))
        password = str(request.args.get('password'))

        current_error = None
        if userid != None and password != None:
            pass_verify = MySQLBase.validatePassword(password, userid)
            if pass_verify == None:
                current_error = 'no_account'
            else:
                return {
                    'verify': pass_verify,
                    'status': 'success'
                }, 200
        else:
            current_error = 'no_id_or_password'    
        
        # password error.
        return {'status': 'error', 'error_code': current_error}