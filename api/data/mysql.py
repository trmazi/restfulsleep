import mysql.connector

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

    def putUserDiscordData(userid: int, discorddata: dict):
        data = {
            'discorddata': discorddata
        }

        cursor = MySQLBase.connection.cursor()
        cursor.execute(f'UPDATE user SET data = {data} WHERE id = {userid}')
        return None