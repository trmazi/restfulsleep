import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from flask_restful import Resource
from flask import request

from api.constants import APIConstants
from api.precheck import RequestPreCheck
from api.data.endpoints.session import SessionData, KeyData
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
            return APIConstants.soft_end('No sessionId was sent!')
        
        decryptedSession = SessionData.AES.decrypt(session_id)
        if not decryptedSession:
            return APIConstants.bad_end('Unable to decrypt SessionId!')

        SessionData.deleteSession(decryptedSession)
        return {'status': 'success'}
    
class emailAuth(Resource):
    server = None
    address = None
    username = None
    password = None

    @staticmethod
    def update_config(config: dict) -> None:
        emailAuth.server = config.get('server')
        emailAuth.address = config.get('address')
        emailAuth.username = config.get('username')
        emailAuth.password = config.get('password')

    def post(self):
        '''
        Given a user's email, validates it, makes a key.
        '''
        data = request.get_json(silent=True)
        if data == None:
            return APIConstants.bad_end('No json data was sent!')
        
        email = data.get('email', None)
        if email == None:
            return APIConstants.bad_end('No email provided.')
        
        user = UserData.getUserByEmail(email)
        if not user:
            return APIConstants.bad_end('No user found.')
        
        if user.get('banned', False):
            return APIConstants.bad_end('You\'re banned.')
        
        auth_key = KeyData.createKey(user.get('id', 0), 'auth_key')
        body = f"Here is your 2FA key\n{auth_key}"

        msg = MIMEMultipart()
        msg['From'] = self.address
        msg['To'] = user.get('email', '')
        msg['Subject'] = "PhaseII Password Reset Request"
        msg.attach(MIMEText(body, 'plain'))

        server = smtplib.SMTP(self.server, 587)
        server.starttls()
        server.login(self.username, self.password)
        server.sendmail(self.address, user.get('email', ''), msg.as_string())
        server.quit()

        return {'status': 'success'}
    
class check2FAKey(Resource):
    def post(self):
        '''
        Given a user's key, validates it, lets user reset password.
        '''
        data = request.get_json(silent=True)
        if data == None:
            return APIConstants.bad_end('No json data was sent!')
        
        key = data.get('key', None)
        if key == None:
            return APIConstants.bad_end('No key provided.')

        try:
            key = int(key)
        except:
            return APIConstants.bad_end('Bad key format.')
        if len(str(key)) != 6:
            return APIConstants.bad_end('Bad key format.')
        
        key_status = KeyData.checkKey(key, 'auth_key')
        if not key_status.get('active', False):
            return APIConstants.bad_end('No key found.')
        
        user = UserData.getUser(key_status.get('id', 0))
        if not user:
            return APIConstants.bad_end('No user found.')
        
        if user.get('banned', False):
            return APIConstants.bad_end('You\'re still banned.')
    
        return {'status': 'success', 'username': user.get('username')}
    
class changePassword(Resource):
    def post(self):
        '''
        Given a user's key, validates it, changes password.
        '''
        data = request.get_json(silent=True)
        if data == None:
            return APIConstants.bad_end('No json data was sent!')
        
        key = data.get('key', None)
        if key == None:
            return APIConstants.bad_end('No key provided.')
        
        newPassword = data.get('newPassword', None)
        if newPassword == None:
            return APIConstants.bad_end('No password provided.')
        
        confirmPassword = data.get('confirmPassword', None)
        if confirmPassword == None:
            return APIConstants.bad_end('No password confirmation provided.')
        
        if len(str(newPassword)) < 8:
            return APIConstants.soft_end('Password must be at least 8 characters!')
        
        if newPassword != confirmPassword:
            return APIConstants.soft_end('The passwords don\'t match!')

        try:
            key = int(key)
        except:
            return APIConstants.bad_end('Bad key format.')
        if len(str(key)) != 6:
            return APIConstants.bad_end('Bad key format.')
        
        key_status = KeyData.checkKey(key, 'auth_key')
        if not key_status.get('active', False):
            return APIConstants.bad_end('No key found.')
        
        user = UserData.getUser(key_status.get('id', 0))
        if not user:
            return APIConstants.bad_end('No user found.')
        
        if user.get('banned', False):
            return APIConstants.bad_end('You\'re still banned.')
        
        KeyData.deleteKey(key, 'auth_key')
        if UserData.resetPassword(user.get('id', 0), newPassword) == True:
            return {'status': 'success'}
        else:
            return APIConstants.bad_end('Failed to reset!')