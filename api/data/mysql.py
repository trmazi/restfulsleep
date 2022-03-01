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
        userdata = MySQLBase.getUser(userid)
        username = userdata[0]
        email = userdata[1]
        admin = userdata[2]

        data = {
            "discorddata": discorddata
        }

        cursor = MySQLBase.connection.cursor()
        cursor.execute(f'UPDATE user SET username = {username}, email = {email}, admin = {admin}, data = {data} WHERE id = {userid}')
        return None