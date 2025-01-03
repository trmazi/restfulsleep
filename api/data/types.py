from sqlalchemy import Column, Integer, String, LargeBinary, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Achievement(Base):
    __tablename__ = 'achievement'
    refid = Column(String(16), primary_key=True)
    id = Column(Integer, primary_key=True)
    type = Column(String(255), primary_key=True)
    data = Column(LargeBinary)

class Arcade(Base):
    __tablename__ = 'arcade'
    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    description = Column(String(255))
    pin = Column(Integer)
    data = Column(LargeBinary)

class ArcadeOwner(Base):
    __tablename__ = 'arcade_owner'
    userid = Column(Integer, primary_key=True)
    arcadeid = Column(Integer, primary_key=True)

class ArcadeSettings(Base):
    __tablename__ = 'arcade_settings'
    arcadeid = Column(Integer, nullable=False, primary_key=True)
    game = Column(String(32), nullable=False, primary_key=True)
    version = Column(Integer, nullable=False, primary_key=True)
    type = Column(String(64), nullable=False, primary_key=True)
    data = Column(LargeBinary, nullable=False)

class Audit(Base):
    __tablename__ = 'audit'
    id = Column(Integer, primary_key=True)
    timestamp = Column(Integer)
    userid = Column(Integer)
    arcadeid = Column(Integer)
    type = Column(String(255))
    data = Column(LargeBinary)

class Balance(Base):
    __tablename__ = 'balance'
    userid = Column(Integer, primary_key=True)
    arcadeid = Column(Integer, primary_key=True)
    balance = Column(Integer)

class Card(Base):
    __tablename__ = 'card'
    id = Column(String(16), primary_key=True)
    userid = Column(Integer)

class Catalog(Base):
    __tablename__ = 'catalog'
    game = Column(String(255), primary_key=True)
    version = Column(Integer, primary_key=True)
    id = Column(Integer, primary_key=True)
    type = Column(String(255))
    data = Column(LargeBinary)

class Client(Base):
    __tablename__ = 'client'
    id = Column(Integer, primary_key=True)
    timestamp = Column(Integer)
    name = Column(String(255))
    token = Column(String(255))

class EditData(Base):
    __tablename__ = 'edit_data'
    id = Column(Integer, primary_key=True)
    song_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, primary_key=True)
    game = Column(String(255))
    data = Column(LargeBinary)

class Extid(Base):
    __tablename__ = 'extid'
    game = Column(String(255), primary_key=True)
    extid = Column(Integer, unique=True)
    userid = Column(Integer, primary_key=True)

class GameSettings(Base):
    __tablename__ = 'game_settings'
    game = Column(String(255), primary_key=True)
    userid = Column(Integer, primary_key=True)
    data = Column(LargeBinary)

class GameUpdates(Base):
    __tablename__ = 'game_updates'
    id = Column(Integer, primary_key=True)
    game = Column(String(255))
    mcode = Column(String(255))
    from_datecode = Column(Integer)
    to_datecode = Column(Integer)
    data = Column(LargeBinary)

class Link(Base):
    __tablename__ = 'link'
    game = Column(String(255), primary_key=True)
    version = Column(Integer, primary_key=True)
    userid = Column(Integer, primary_key=True)
    type = Column(String(255), primary_key=True)
    other_userid = Column(Integer, primary_key=True)
    data = Column(LargeBinary)

class Lobby(Base):
    __tablename__ = 'lobby'
    id = Column(Integer, primary_key=True)
    game = Column(String(255))
    version = Column(Integer)
    userid = Column(Integer)
    time = Column(Integer)
    data = Column(LargeBinary)

class Machine(Base):
    __tablename__ = 'machine'
    id = Column(Integer, primary_key=True)
    pcbid = Column(String(20), unique=True)
    name = Column(String(255))
    description = Column(String(255))
    arcadeid = Column(Integer)
    port = Column(Integer, unique=True)
    game = Column(String(255))
    version = Column(Integer)
    data = Column(LargeBinary)
    updaton = Column(Boolean)

class Music(Base):
    __tablename__ = 'music'
    id = Column(Integer)
    songid = Column(Integer, primary_key=True)
    chart = Column(Integer, primary_key=True)
    game = Column(String(255), primary_key=True)
    version = Column(Integer, primary_key=True)
    name = Column(String(255))
    artist = Column(String(255))
    genre = Column(String(255))
    data = Column(LargeBinary)

class News(Base):
    __tablename__ = 'news'
    id = Column(Integer, primary_key=True)
    timestamp = Column(Integer)
    title = Column(String(255))
    body = Column(String)
    data = Column(LargeBinary)

class Profile(Base):
    __tablename__ = 'profile'
    refid = Column(String(255), ForeignKey('refid.refid'), primary_key=True)
    data = Column(LargeBinary)

class Refid(Base):
    __tablename__ = 'refid'
    refid = Column(String(255), primary_key=True)
    userId = Column(Integer, ForeignKey('user.id'))
    game = Column(String(255))
    version = Column(Integer)

class Score(Base):
    __tablename__ = 'score'
    id = Column(Integer, primary_key=True)
    userid = Column(Integer)
    musicid = Column(Integer, primary_key=True)
    points = Column(Integer)
    timestamp = Column(Integer)
    update = Column(Integer)
    lid = Column(Integer, primary_key=True)
    data = Column(LargeBinary)

class Attempt(Base):
    __tablename__ = 'score_history'
    id = Column(Integer, primary_key=True)
    userid = Column(Integer)
    musicid = Column(Integer, primary_key=True)
    points = Column(Integer)
    timestamp = Column(Integer)
    new_record = Column(Boolean)
    lid = Column(Integer, primary_key=True)
    data = Column(LargeBinary)

class Session(Base):
    __tablename__ = 'session'
    session = Column(String(255), primary_key=True)
    id = Column(Integer)
    type = Column(String(255))
    expiration = Column(Integer)

class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    username = Column(String(255), unique=True)
    email = Column(String(255))
    password = Column(String(255))
    pin = Column(String(4), primary_key=False)
    admin = Column(Boolean)
    banned = Column(Boolean)
    data = Column(LargeBinary)

class UserContent(Base):
    __tablename__ = 'user_content'
    id = Column(Integer, primary_key=True)
    game = Column(String(255))
    version = Column(Integer)
    userid = Column(Integer)
    type = Column(String(255))
    data = Column(LargeBinary)
    sessionid = Column(String(255))
    musicid = Column(Integer)
    timestamp = Column(Integer)