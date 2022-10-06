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
                return bad_end('no account.')

            if password != None:
                pass_verify = MySQLBase.validatePassword(password, userID[0])
                if pass_verify == None:
                    return bad_end('no account.')
            
                if pass_verify:
                    aes = AESCipher('restful_crypto_that_shouldnt_be_hardcoded')
                    session = MySQLBase.createSession(userID[0], 'userid', 90 * 86400)
                    return {'status': 'success', 'session_id': aes.encrypt(session), 'userid': userID[0]}

                else: return bad_end('wrong password.')

        return bad_end('there was an issue in your request.')

class deleteUserSession(Resource):
    def post(self):
        '''
        Given a user's session id, delete it from the db.
        '''
        session_id = request.get_json(silent=True)
        def bad_end(error):
            return {'status': 'error', 'error_code': error}
        
        if session_id == None:
            return bad_end('No json data was sent!')
        
        session_id = session_id.get('sessionID', None)
        if session_id == None:
            return bad_end('No sessionID was sent!')

        MySQLBase.deleteSession(session_id)
        return {'status': 'success'}

class getGameProfile(Resource):
    '''
    Given a game, version, and userid. 
    If user exists, return their profile.
    '''
    def get(self):
        game = request.headers.get('game', None)
        version = request.headers.get('version', None)
        userid = request.headers.get('userid', None)

        def bad_end(error):
            return {'status': 'error', 'error_code': error}

        if game == None:
            return(bad_end('No game code was provided'))
        if version == None:
            return(bad_end('No game version was provided'))
        if userid == None:
            return(bad_end('No userid provided'))

        data = MySQLBase.getProfile(game, version, userid)
        if data == None:
            return(bad_end('no profile'))

        if data['status'] == 'error':
            return(bad_end(data['error_code']))

        return(data)