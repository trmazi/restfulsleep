from flask import request
from typing import Tuple, Dict
from api.constants import APIConstants
from api.data.endpoints.session import SessionData
from api.data.endpoints.user import UserData

class RequestPreCheck():
    def getSession() -> Tuple[bool, Dict]:
        '''
        Checks a user's session via a their auth key. Key is sent in headers as `User-Auth-Key`.
        Returns a tuple of a bool representing session state and a dict containing either a session or an error code.
        '''
        userAuthCode = request.headers.get('User-Auth-Key')
        if not userAuthCode:
            return (False, APIConstants.bad_end('No user auth provided!'))
        
        decryptedSession = None
        try:
            decryptedSession = SessionData.AES.decrypt(userAuthCode)
        except:
            return (False, APIConstants.bad_end('Unable to decrypt SessionId!'))
        
        if not decryptedSession:
            return (False, APIConstants.bad_end('Unable to decrypt SessionId!'))

        session = SessionData.checkSession(decryptedSession)
        if session.get('active') != True:
            return (False, APIConstants.bad_end('Invalid user session!'))
        
        return (True, session)
    
    def checkAdmin(session: Dict) -> Tuple[bool, Dict]:
        '''
        Check if a user is an admin. Returns a bool and a response dict.
        '''
        userId = session.get('id', 0)
        user = UserData.getUser(userId)

        if not user.get("admin", False):
            return (False, APIConstants.bad_end('You must have administrative rights.'))
        
        return (True, None)