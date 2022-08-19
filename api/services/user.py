from flask_restful import Resource, reqparse
from flask import request

from api.data.mysql import MySQLBase
from api.data.aes import AESCipher

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

class logUserIn(Resource):
    def get(self):
        '''
        Gets a user's username and password, validates them, makes a session.
        '''
        password = request.headers.get('password', None)
        username = request.headers.get('username', None)

        def bad_end(error):
            return {'status': 'error', 'error_code': error}

        if username != None:
            userID = MySQLBase.getUserFromName(username)
            if userID == None:
                bad_end('no account.')

            if password != None:
                pass_verify = MySQLBase.validatePassword(password, userID[0])
                if pass_verify == None:
                    bad_end('no account.')
            
                if pass_verify:
                    aes = AESCipher('restful_crypto_that_shouldnt_be_hardcoded')
                    session = MySQLBase.createSession(userID[0], 'userid', 90 * 86400)
                    print(session)
                else: bad_end('wrong password.')

            
        bad_end('there was an issue in your request.')