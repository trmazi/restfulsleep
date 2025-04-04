from flask import request
from typing import Tuple
from api.constants import APIConstants, ValidatedDict
from api.data.endpoints.session import SessionData
from api.data.endpoints.user import UserData

class RequestPreCheck():
    def getSession() -> Tuple[bool, ValidatedDict]:
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
    
    def checkAdmin(session: ValidatedDict) -> Tuple[bool, ValidatedDict]:
        '''
        Check if a user is an admin. Returns a bool and a response dict.
        '''
        userId = session.get('id', 0)
        user = UserData.getUser(userId)

        if not user.get("admin", False):
            return (False, APIConstants.bad_end('You must have administrative rights.'))
        
        return (True, None)
    
    def checkData(keys: dict[str, type] = {}) -> Tuple[bool, ValidatedDict]:
        '''
        Check if JSON data was sent. If found, return it as a ValidatedDict.

        Optionally can be given a dict of {key: type} to check for specific elements.
        Returns an error for the missing/incorrect keys.
        '''
        data = request.get_json(silent=True)
        if data is None:
            return False, APIConstants.bad_end("No JSON data was sent!")

        data = ValidatedDict(data)

        type_getters = {
            str: data.get_str,
            int: data.get_int,
            bool: data.get_bool,
            bytes: data.get_bytes,
        }

        for key, key_type in keys.items():
            getter = type_getters.get(key_type)
            if getter and getter(key) is None:
                return False, APIConstants.bad_end(f"{key}: {key_type.__name__} not found!")

        return True, data
    
    def checkArgs(keys: dict[str, type] = {}) -> Tuple[bool, ValidatedDict]:
        '''
        Check if args were sent. If found, return them as a ValidatedDict.

        Optionally can be given a dict of {key: type} to check for specific elements.
        Returns an error for the missing/incorrect keys.
        '''
        data = request.args
        if data is None:
            return False, APIConstants.bad_end("No args sent!")

        data = ValidatedDict(data)

        type_getters = {
            str: data.get_str,
            int: data.get_int,
            bool: data.get_bool,
            bytes: data.get_bytes,
        }

        for key, key_type in keys.items():
            getter = type_getters.get(key_type)
            if getter and getter(key) is None:
                return False, APIConstants.bad_end(f"{key}: {key_type.__name__} not found!")

        return True, data