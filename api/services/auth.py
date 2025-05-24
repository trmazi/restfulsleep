from flask_restful import Resource

from api.constants import APIConstants
from api.precheck import RequestPreCheck
from api.data.endpoints.session import SessionData, KeyData
from api.data.endpoints.user import UserData

from api.external.mailjet import MailjetSMTP

class UserSession(Resource):
    def get(self):
        sessionState, session = RequestPreCheck.getSession()
        if not sessionState:
            return session
        
        return {'status': 'success', 'activeSession': session.get_bool('active'), 'userId': session.get_int('id')}
    
    def post(self):
        '''
        Given a user's username and password, validates them, makes a session.
        '''
        dataState, data = RequestPreCheck.checkData({
            'username': str,
            'password': str,
        })
        if not dataState:
            return data
        
        username = data.get_str('username')
        password = data.get_str('password')
        if username == '' or password == '':
            return APIConstants.soft_end('No credentials provided.')
        
        user = UserData.getUserByName(username)
        if not user:
            return APIConstants.soft_end('Password incorrect or no user found.')
        userId = user.get_int('id')

        if UserData.validatePassword(password, userId):
            sessionID = SessionData.createSession(userId, 'userid', 90 * 86400)
            return {'status': 'success', 'sessionId': SessionData.AES.encrypt(sessionID), 'userId': userId}
        else:
            return APIConstants.soft_end('Password incorrect or no user found.')
    
    def delete(self):
        '''
        Given a user's session id, delete it from the db.
        '''
        dataState, data = RequestPreCheck.checkData()
        if not dataState:
            return data
        
        session_id = data.get_str('sessionId')
        if session_id != '':
            decryptedSession = SessionData.AES.decrypt(session_id)
            if not decryptedSession:
                return APIConstants.bad_end('Unable to decrypt SessionId!')

            SessionData.deleteSession(decryptedSession)
        return {'status': 'success'}
    
class emailAuth(Resource):
    def post(self):
        '''
        Given a user's email, validates it, makes a key.
        '''
        dataState, data = RequestPreCheck.checkData({
            'email': str
        })
        if not dataState:
            return data
        
        email = data.get_str('email')
        if email == '':
            return APIConstants.soft_end('No email provided.')
        
        user = UserData.getUserByEmail(email)
        if not user:
            return APIConstants.soft_end('No user found.')
        
        if user.get_bool('banned'):
            return APIConstants.bad_end('You\'re banned.')
        
        authKey = KeyData.createKey(user.get_int('id'), 'auth_key')
        errorState = MailjetSMTP().sendAuthKey(user.get_str('email'), authKey)
        if errorState:
            return APIConstants.bad_end(errorState)

        return {'status': 'success'}
    
class check2FAKey(Resource):
    def post(self):
        '''
        Given a user's key, validates it, lets user reset password.
        '''
        dataState, data = RequestPreCheck.checkData({
            'key': str
        })
        if not dataState:
            return data
        
        key = data.get_str('key')

        if len(key) != 6:
            return APIConstants.bad_end('Incorrect key length.')
        
        key_status = KeyData.checkKey(key, 'auth_key')
        if not key_status.get_bool('active'):
            return APIConstants.bad_end('No key found.')
        
        user = UserData.getUser(key_status.get_int('id'))
        if not user:
            return APIConstants.bad_end('No user found.')
        
        if user.get_bool('banned'):
            return APIConstants.bad_end('You\'re still banned.')
    
        return {'status': 'success', 'username': user.get('username')}
    
class resetPassword(Resource):
    def post(self):
        '''
        Given a user's key, validates it, changes password.
        '''
        dataState, data = RequestPreCheck.checkData({
            'key': str, 
            'newPassword': str,
            'confirmPassword': str,
        })
        if not dataState:
            return data
        
        key = data.get_str('key')
        
        newPassword = data.get_str('newPassword')
        if newPassword == '':
            return APIConstants.bad_end('No password provided.')
        
        confirmPassword = data.get_str('confirmPassword')
        if confirmPassword == '':
            return APIConstants.bad_end('No password confirmation provided.')
        
        if len(newPassword) < 8:
            return APIConstants.soft_end('Password must be at least 8 characters!')
        
        if newPassword != confirmPassword:
            return APIConstants.soft_end('The passwords don\'t match!')

        if len(key) != 6:
            return APIConstants.bad_end('Bad key format.')
        
        key_status = KeyData.checkKey(key, 'auth_key')
        if not key_status.get_bool('active'):
            return APIConstants.bad_end('No key found.')
        
        user = UserData.getUser(key_status.get_int('id'))
        if not user:
            return APIConstants.bad_end('No user found.')
        
        if user.get_bool('banned'):
            return APIConstants.bad_end('You\'re still banned.')
        
        KeyData.deleteKey(key, 'auth_key')
        if UserData.updatePassword(user.get_int('id'), newPassword) == True:
            errorState = MailjetSMTP().passwordChanged(user.get_str('email'))
            if errorState:
                return APIConstants.bad_end(errorState)

            return {'status': 'success'}
        else:
            return APIConstants.bad_end('Failed to reset!')