from typing import Dict
import mysql.connector
from passlib.hash import pbkdf2_sha512
import random
import time

from api.data.json import JsonEncoded

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
        data = cursor.fetchall()
        cursor.close()

        return data

    def getUser(userid: int):
        cursor = MySQLBase.connection.cursor()
        cursor.execute(f'SELECT username, email, admin, data FROM user WHERE id = {userid}')
        data = cursor.fetchone()
        cursor.close()

        return data

    def getUserFromName(username: str) -> int:
        cursor = MySQLBase.connection.cursor()
        cursor.execute(f'SELECT id FROM user WHERE username = "{username}"')
        data = cursor.fetchone()
        cursor.close()

        return data

    def getProfile(game: str, version: int, userid: int) -> Dict:
        '''
        Pull a user's profile.
        '''
        cursor = MySQLBase.connection.cursor()
        sql = (
            "SELECT refid FROM refid" +
            f'WHERE userid = {userid} AND game = "{game}" AND version = {version}'
        )
        cursor.execute(sql)
        data = cursor.fetchone()
        if data == None:
            return {'status': 'error', 'error_code': 'no profile'}

        profile = {
            'refid': data['refid'],
            'game': game,
            'version': version,
        }

        sql = f"SELECT data FROM profile WHERE refid = '{data['refid']}'"
        cursor.execute(sql)
        data = cursor.fetchone()
        if data == None:
            return {'status': 'error', 'error_code': 'no profile'}

        cursor.close()
        return(JsonEncoded.deserialize(data['data']))

    def validatePassword(plain_password: str, userID: int) -> bool:
        cursor = MySQLBase.connection.cursor()
        cursor.execute(f'SELECT password FROM user WHERE id = {userID}')
        pw_hash = cursor.fetchone()
        cursor.close()
        if pw_hash == None:
            return False
        pw_hash = pw_hash[0]

        try:
            # Verifying the password
            return pbkdf2_sha512.verify(plain_password, pw_hash)
        except (ValueError, TypeError):
            return False

    def createSession(opid: int, optype: str, expiration: int=(30 * 86400)) -> str:
        """
        Given an ID, create a session string.

        Parameters:
            opid - ID we wish to start a session for.
            expiration - Number of seconds before this session is invalid.

        Returns:
            A string that can be used as a session ID.
        """
        # Create a new session that is unique
        while True:
            session = ''.join(random.choice('0123456789ABCDEF') for _ in range(32))

            cursor = MySQLBase.connection.cursor()
            cursor.execute(f'SELECT session FROM session WHERE session = "{session}"')
            data = cursor.fetchone()
            
            if data == None:
                # Make sure sessions expire in a reasonable amount of time
                expiration = int(time.time() + expiration)

                # Use that session
                sql = (
                    "INSERT INTO session (id, session, type, expiration) " +
                    f"VALUES ({opid}, '{session}', '{optype}', {expiration})"
                )
                cursor.execute(sql)

                cursor.execute(f'SELECT session FROM session WHERE session = "{session}"')
                data = cursor.fetchone()
                cursor.close()
                if data != None:
                    return session

    def deleteSession(sessionID: str) -> None:
        '''
        Destroy a previously-created session.

        Parameters:
            sessionID - A session id string as returned from create_session.
        '''
        # Remove the session token
        cursor = MySQLBase.connection.cursor()
        cursor.execute(f"DELETE FROM session WHERE session = '{sessionID}' AND type = 'userid'")
        cursor.close()