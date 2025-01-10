import sqlite3
import random

class CasinoDB:
    def __init__(self, db_file): # Исправлено: init -> __init__
        self.conn = sqlite3.connect(db_file)
        self.cursor = self.conn.cursor()
        self.create_table()

    def create_table(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                balance REAL DEFAULT 0.0
            )
        ''')
        self.conn.commit()

    def get_balance(self, user_id):
        self.cursor.execute("SELECT balance FROM users WHERE id = ?", (user_id,))
        result = self.cursor.fetchone()
        return result[0] if result else 0.0

    def update_balance(self, user_id, amount):
        try:
            self.cursor.execute("UPDATE users SET balance = balance + ? WHERE id = ?", (amount, user_id))
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Ошибка обновления баланса: {e}")
            return False

    def add_user(self, user_id):
        try:
            self.cursor.execute("INSERT INTO users (id, balance) VALUES (?, ?)", (user_id, 0.0))
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Ошибка добавления пользователя: {e}")
            return False

    def close(self):
        self.conn.close()

    def update_balance_admin(self, user_id, new_balance):
        try:
            self.cursor.execute("UPDATE users SET balance = ? WHERE id = ?", (new_balance, user_id))
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Ошибка обновления баланса: {e}")
            return False

