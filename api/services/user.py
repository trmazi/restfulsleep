from flask_restful import Resource
from flask import request

from api.constants import APIConstants
from api.data.endpoints.user import UserData
from api.data.endpoints.session import SessionData

class getUserAccount(Resource):
    '''
    Given a user ID, return a user's public info.
    '''
    def get(self, userId):
        user = UserData.getUser(int(userId))
        if not user:
            return APIConstants.bad_end('No user found.')
        
        userAuthCode = request.headers.get('User-Auth-Key')
        authUser = False;
        if userAuthCode:
            decryptedSession = None
            try:
                decryptedSession = SessionData.AES.decrypt(userAuthCode)
            except:
                return APIConstants.bad_end('Unable to decrypt SessionId!')
            if not decryptedSession:
                return APIConstants.bad_end('Unable to decrypt SessionId!')

            session = SessionData.checkSession(decryptedSession)
            if session.get('active') == True and user.get('id', 0) == session.get('id', -1):
                authUser = True
        userData = user.get('data', {})
        discordLink = userData.get('discord', {})
        avatar = None
        if discordLink.get('linked', False):
            avatar = f"https://cdn.discordapp.com/avatars/{discordLink.get('id')}/{discordLink.get('avatar')}"

        return {
            'status': 'success',
            'user': {
                'id': user['id'],
                'name': user['username'],
                'email': user['email'] if authUser else None,
                'admin': user['admin'],
                'banned': user['banned'],
                'avatar': avatar,
                'data': user['data'] if authUser else None,
            }
        }

class getGameProfile(Resource):
    '''
    Given a game, version, and userid. 
    If user exists, return their profile.
    '''
    def get(self):
        game = request.headers.get('game', None)
        version = int(request.headers.get('version', None))
        userid = int(request.headers.get('userid', None))
        just_stats = request.headers.get('stats', None)
        print(just_stats)

        def bad_end(error):
            return {'status': 'error', 'error_code': error}

        if game == None:
            return(bad_end('No game code was provided'))
        if version == None:
            return(bad_end('No game version was provided'))
        if userid == None:
            return(bad_end('No userid provided'))

        data = {}

        if data == None:
            return(bad_end('no profile'))

        if data['status'] == 'error':
            return(bad_end(data['error_code']))

        return(data)