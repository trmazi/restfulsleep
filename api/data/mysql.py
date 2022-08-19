import mysql.connector
import json
from passlib.hash import pbkdf2_sha512
import random
import time

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
        #cursor.execute(f'SELECT password FROM user WHERE id = {userID}')
        pw_hash = cursor.fetchone()
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

            if cursor.fetchone() == None:
                # Make sure sessions expire in a reasonable amount of time
                expiration = int(time.time() + expiration)

                # Use that session
                sql = (
                    "INSERT INTO session (id, session, type, expiration) " +
                    f"VALUES ({opid}, '{session}', '{optype}', {expiration})"
                )
                cursor.execute(sql)

                cursor.execute(f'SELECT session FROM session WHERE session = "{session}"')
                if cursor.fetchone() != None:
                    return session