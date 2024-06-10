from passlib.hash import pbkdf2_sha512

from api.data.json import JsonEncoded
from api.data.mysql import MySQLBase
from api.data.types import User, Card

class UserData:
    def validatePassword(plain_password: str, userID: int) -> bool:
        with MySQLBase.SessionLocal() as session:
            pw_hash = session.query(User.password).filter(User.id == userID).first()
            if not pw_hash:
                return False
            try:
                return pbkdf2_sha512.verify(plain_password, pw_hash[0])
            except (ValueError, TypeError):
                return False

    def getUser(userId: int) -> dict:
        with MySQLBase.SessionLocal() as session:
            user = session.query(User).filter(User.id == userId).first()
            if user is None:
                return None
            else:
                return {
                    'id': int(user.id),
                    'username': user.username,
                    'email': user.email,
                    'admin': bool(user.admin),
                    'banned': bool(user.banned),
                    'data': JsonEncoded.deserialize(user.data)
                }

    def getUserByName(username: str) -> dict:
        with MySQLBase.SessionLocal() as session:
            user = session.query(User).filter(User.username == username).first()
            if user is None:
                return None
            else:
                return {
                    'id': int(user.id),
                    'username': user.username,
                    'admin': bool(user.admin),
                    'banned': bool(user.banned),
                    'data': JsonEncoded.deserialize(user.data)
                }
            
    def getCards(userId: int) -> dict:
        with MySQLBase.SessionLocal() as session:
            cards = session.query(Card).filter(Card.userid == userId).all()
            if cards is None:
                return None
            else:
                return [card.id for card in cards]