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
            
    def updateUser(userId: int, newUsername: str = None, newEmail: str = None, newPin: str = None) -> bool:
        with MySQLBase.SessionLocal() as session:
            user = session.query(User).filter(User.id == userId).first()
            if user is None:
                return False
            else:
                didAnything = False
                if newUsername:
                    user.username = newUsername
                    didAnything = True

                if newEmail:
                    user.email = newEmail
                    didAnything = True

                if newPin:
                    user.pin = newPin
                    didAnything = True

                if didAnything:
                    session.commit()
                    return True

                return False
       
    def updatePassword(userId: int, newPassword: str) -> bool:
        with MySQLBase.SessionLocal() as session:
            user = session.query(User).filter(User.id == userId).first()
            if user is None:
                return False
            else:
                hashed = pbkdf2_sha512.hash(newPassword)
                user.password = hashed
                session.commit()
                return True

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
    
    def getUserByEmail(email: str) -> dict:
        with MySQLBase.SessionLocal() as session:
            user = session.query(User).filter(User.email == email).first()
            if user is None:
                return None
            else:
                return {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'banned': bool(user.banned),
                }

    def getCards(userId: int) -> dict:
        with MySQLBase.SessionLocal() as session:
            cards = session.query(Card).filter(Card.userid == userId).all()
            if cards is None:
                return None
            else:
                return [card.id for card in cards]
            
    def cardExist(cardId: str) -> bool:
        with MySQLBase.SessionLocal() as session:
            card = session.query(Card).filter(Card.id == cardId).first()
            if card is None:
                return False
            else:
                return True

    def putCard(userId: int, cardId: str) -> bool:
        with MySQLBase.SessionLocal() as session:
            if session.query(Card).filter(Card.id == cardId).first() is not None:
                return False

            new_card = Card(id=cardId, userid=userId)
            session.add(new_card)
            session.commit()
            return True

    def deleteCard(userId: str, cardId: str) -> bool:
        with MySQLBase.SessionLocal() as session:
            card = session.query(Card).filter(Card.id == cardId, Card.userid == userId).first()
            if card is None:
                return True

            session.delete(card)
            session.commit()
            return True