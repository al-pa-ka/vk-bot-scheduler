import sqlite3


def get_last_status():
    con = sqlite3.connect('database.sqlite3')
    cursor = con.cursor()
    cursor.execute('SELECT day, mounth, year FROM last_status ORDER BY id DESC;')
    result = cursor.fetchone()
    cursor.close()
    con.close()
    return result


def save_last_status(day, month, year):
    con = sqlite3.connect('database.sqlite3')
    cursor = con.cursor()
    cursor.execute(f'INSERT INTO last_status(day, mounth, year) VALUES({int(day)}, {int(month)}, {int(year)});')
    con.commit()
    cursor.close()
    con.close()


def get_token(token_name):
    con = sqlite3.connect('database.sqlite3')
    cursor = con.cursor()
    cursor.execute(f'SELECT token FROM tokens WHERE token_name="{token_name}";')
    result = cursor.fetchone()
    cursor.close()
    con.close()
    return result[0]


class DataBase:
    def __init__(self):
        self.connection = sqlite3.connect('database.sqlite3')

    async def add_user(self, user_id: int):
        cursor = self.connection.cursor()
        cursor.execute(f'INSERT INTO users(user_id) VALUES({user_id});')
        self.connection.commit()
        cursor.close()

    async def get_all_users(self):
        cursor = self.connection.cursor()
        cursor.execute(f'SELECT user_id FROM users;')
        result = cursor.fetchall()
        cursor.close()
        return result

    async def is_user_subscribed(self, user_id: int):
        cursor = self.connection.cursor()
        cursor.execute(f'SELECT user_id FROM users WHERE user_id="{user_id}";')
        result = cursor.fetchall()
        cursor.close()
        if result:
            return True
        return False
