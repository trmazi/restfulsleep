import mysql.connector

class MySQLBase():
    def pull(type:str):
        connection = mysql.connector.connect(
            host="localhost",
            user="bemani",
            password="bemani",
            database="bemani"
        )
        cursor = connection.cursor()
        cursor.execute(f'SELECT * FROM {type}')

        return cursor.fetchall()

    def push(type:str):
        return None