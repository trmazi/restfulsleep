import random
import time
from typing import Dict, Any
from api.data.aes import AESCipher
from api.data.types import Session
from api.data.mysql import MySQLBase
from api.constants import ValidatedDict

class SessionData:
    AES = None

    @staticmethod
    def updateConfig(cryptoConfig: Dict[str, Any]) -> None:
        key = cryptoConfig.get('cookie_key', None)
        if not key:
            raise Exception("Failed to initialize cookie encryption.")
        
        SessionData.AES = AESCipher(key)

    def createSession(opId: int, opType: str, expiration: int=(30 * 86400)) -> str:
        session_token = ''.join(random.choice('0123456789ABCDEF') for _ in range(32))
        expiration_time = int(time.time() + expiration)

        with MySQLBase.SessionLocal() as session:
            while session.query(Session).filter(Session.session == session_token).first():
                session_token = ''.join(random.choice('0123456789ABCDEF') for _ in range(32))
            
            new_session = Session(id=opId, session=session_token, type=opType, expiration=expiration_time)
            session.add(new_session)
            session.commit()

            return session_token
        
    def checkSession(sessionID: str) -> ValidatedDict:
        with MySQLBase.SessionLocal() as session:
            userSession = session.query(Session).filter(Session.session == sessionID, Session.type == 'userid').first()
            if userSession != None:
                return ValidatedDict({
                    'active': True,
                    'id': int(userSession.id)
                })
            else:
                return ValidatedDict({
                    'active': False,
                    'id': None 
                })
        
    def deleteSession(sessionID: str) -> None:
        with MySQLBase.SessionLocal() as session:
            session.query(Session).filter(Session.session == sessionID, Session.type == 'userid').delete()
            session.commit()

class KeyData:
    def createKey(opId: int, opType: str, expiration: int=(300)) -> str:
        key_token = ''.join(random.choice('123456789') for _ in range(6))
        expiration_time = int(time.time() + expiration)

        with MySQLBase.SessionLocal() as session:
            while session.query(Session).filter(Session.session == key_token).first():
                key_token = ''.join(random.choice('123456789') for _ in range(6))
            
            new_session = Session(id=opId, session=key_token, type=opType, expiration=expiration_time)
            session.add(new_session)
            session.commit()

            return key_token
        
    def checkKey(key: int, opType: str) -> ValidatedDict:
        with MySQLBase.SessionLocal() as session:
            userSession = session.query(Session).filter(Session.session == key, Session.type == opType).first()
            if userSession != None:
                return ValidatedDict({
                    'active': True,
                    'id': int(userSession.id)
                })
            else:
                return ValidatedDict({
                    'active': False,
                    'id': None 
                })
        
    def deleteKey(key: str, opType: str) -> None:
        with MySQLBase.SessionLocal() as session:
            session.query(Session).filter(Session.session == key, Session.type == opType).delete()
            session.commit()