import mysql.connector
import json
from passlib.hash import pbkdf2_sha512

class MySQLBase():
    connection = mysql.connector.connect(
        host="localhost",
        user="bemani",
        password="bemani",
        database="bemani"
    )

    def pull(type:str):
        cursor = MySQLBase.connection.cursor()
        cursor.execute(f'SELECT * FROM {type}')

        return cursor.fetchall()

    def getUser(userid: int):
        cursor = MySQLBase.connection.cursor()
        cursor.execute(f'SELECT username, email, admin, data FROM user WHERE id = {userid}')
        return cursor.fetchone()

    def getUserFromName(username: str) -> int:
        cursor = MySQLBase.connection.cursor()
        cursor.execute(f'SELECT id FROM user WHERE username = "{username}"')
        return cursor.fetchone()

    def validatePassword(plain_password: str, userID: int) -> bool:
        cursor = MySQLBase.connection.cursor()
        cursor.execute(f'SELECT password FROM user WHERE id = {userID}')
        pw_hash = cursor.fetchone()[0] if cursor.fetchone() != None else None
        if pw_hash == None:
            return False

        try:
            # Verifying the password
            return pbkdf2_sha512.verify(plain_password, pw_hash)
        except (ValueError, TypeError):
            return False

    def putUserDiscordData(userid: int, discorddata: dict):
        userdata = MySQLBase.getUser(userid)
        username = userdata[0]
        email = userdata[1]
        admin = userdata[2]

        data = {
            "discorddata": discorddata
        }

        data = json.dumps(data)

        cursor = MySQLBase.connection.cursor()
        cursor.execute(f'UPDATE user SET username = {username}, email = {email}, admin = {admin} WHERE id = {userid}')
        return None