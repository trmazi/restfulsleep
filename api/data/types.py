from sqlalchemy import Column, Integer, String, LargeBinary, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    username = Column(String(255), unique=True)
    email = Column(String(255))
    password = Column(String(255))
    admin = Column(Boolean)
    banned = Column(Boolean)
    data = Column(LargeBinary)

class Card(Base):
    __tablename__ = 'card'
    id = Column(Integer, primary_key=True)
    userid = Column(Integer)

class News(Base):
    __tablename__ = 'news'
    id = Column(Integer, primary_key=True)
    timestamp = Column(Integer)
    title = Column(String(255))
    body = Column(String)
    data = Column(LargeBinary)

class Refid(Base):
    __tablename__ = 'refid'
    refid = Column(String(255), primary_key=True)
    userId = Column(Integer, ForeignKey('user.id'))
    game = Column(String(255))
    version = Column(Integer)

class Profile(Base):
    __tablename__ = 'profile'
    refid = Column(String(255), ForeignKey('refid.refid'), primary_key=True)
    data = Column(LargeBinary)

class GameSettings(Base):
    __tablename__ = 'game_settings'
    id = Column(Integer, primary_key=True)
    game = Column(String(255))
    userId = Column(Integer, ForeignKey('user.id'))
    data = Column(LargeBinary)

class Session(Base):
    __tablename__ = 'session'
    session = Column(String(255), primary_key=True)
    id = Column(Integer)
    type = Column(String(255))
    expiration = Column(Integer)