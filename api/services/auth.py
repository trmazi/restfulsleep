from flask_restful import Resource
from flask import request

from api.constants import APIConstants
from api.precheck import RequestPreCheck
from api.data.endpoints.session import SessionData
from api.data.endpoints.user import UserData

class createUserSession(Resource):
    def post(self):
        '''
        Given a user's username and password, validates them, makes a session.
        '''
        data = request.get_json(silent=True)
        if data == None:
            return APIConstants.bad_end('No json data was sent!')
        
        username = data.get('username', None)
        password = data.get('password', None)

        if username == None or password == None:
            return APIConstants.bad_end('No credentials provided.')
        
        user = UserData.getUserByName(username)
        if not user:
            return APIConstants.bad_end('Password incorrect or no user found.')
        
        if UserData.validatePassword(password, user.get('id', 0)):
            sessionID = SessionData.createSession(user.get('id', 0), 'userid', 90 * 86400)
            return {'status': 'success', 'sessionId': SessionData.AES.encrypt(sessionID), 'userId': user.get('id', 0)}
        else:
            return APIConstants.bad_end('Password incorrect or no user found.')

class checkUserSession(Resource):
    def post(self):
        '''
        Given a user's session id, check if it's in the db.
        '''
        sessionState, session = RequestPreCheck.getSession()
        if not sessionState:
            return session
        
        return {'status': 'success', 'activeSession': session.get('active', False), 'userId': session.get('id', 0)}

class deleteUserSession(Resource):
    def post(self):
        '''
        Given a user's session id, delete it from the db.
        '''
        data = request.get_json(silent=True)
        if data == None:
            return APIConstants.bad_end('No json data was sent!')
        
        session_id = data.get('sessionId', None)
        if session_id == None:
            return APIConstants.bad_end('No sessionId was sent!')
        
        decryptedSession = SessionData.AES.decrypt(session_id)
        if not decryptedSession:
            return APIConstants.bad_end('Unable to decrypt SessionId!')

        SessionData.deleteSession(decryptedSession)
        return {'status': 'success'}