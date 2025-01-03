import random

from api.data.types import UserContent
from api.data.mysql import MySQLBase

class ShareData:
    def getNextSession() -> str:
        session_token = ''.join(random.choice('0123456789ABCDEF') for _ in range(16))

        with MySQLBase.SessionLocal() as session:
            while session.query(UserContent).filter(UserContent.sessionid == session_token).first():
                session_token = ''.join(random.choice('0123456789ABCDEF') for _ in range(16))

            return session_token
