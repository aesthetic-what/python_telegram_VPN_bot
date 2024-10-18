
import sqlite3

class DataBase:
    def __init__(self, db_file):
        self.connect = sqlite3.connect(db_file)
        self.cursor = self.connect.cursor()

    async def get_info(self):
        with self.connect:
            return self.cursor.execute("""SELECT * FROM users""").fetchall()
    
    async def get_user_id_data(self):
        with self.connect:
            return self.cursor.execute("""SELECT user_id, date_buy FROM users""").fetchall()

    async def add_user(self, user_id, name):
        with self.connect:
            return self.cursor.execute("""INSERT INTO users (user_id, username, role) VALUES (?, ?, ?)""", 
                                       (user_id, name, 'admin' if user_id == 863618184 else 'user'))
        
    async def update_label(self, label, user_id):
        with self.connect:
            return self.cursor.execute("""UPDATE users SET label=(?) WHERE user_id=(?)""", (label, user_id, ))
        
    async def get_payment_status(self, user_id):
        with self.connect:
            return self.cursor.execute("""SELECT bought, label FROM users WHERE user_id=(?)""", (user_id, )).fetchall()
        
    async def update_payment_status(self, user_id, test):
        with self.connect:
            return self.cursor.execute("""UPDATE users SET bought=(?) WHERE user_id=(?)""", (test, user_id, ))
        
    async def check_vpn_key(self, user_id):
        with self.connect:
            return self.cursor.execute("""SELECT vpn_key FROM users WHERE user_id=(?)""", (user_id, )).fetchall()
        
    async def add_vpn_key(self, vpn, user_id):
        with self.connect:
            return self.cursor.execute("""UPDATE users SET vpn_key=(?) WHERE user_id=(?)""", (vpn, user_id))
        
    async def take_vpn_key(self, user_id):
        with self.connect:
            return self.cursor.execute("""SELECT vpn_key FROM users WHERE user_id=(?)""", (user_id, )).fetchall()
        
    async def delete_user(self, user_id):
        with self.connect:
            return self.cursor.execute("""DELETE users WHERE user_id=(?)""", (user_id, ))
    
    async def check_sub(self, user_id):
        with self.connect:
            return self.cursor.execute("SELECT date_buy FROM users WHERE user_id=(?)", (user_id,)).fetchone()
        
    async def add_sub_1month(self, user_id):
        with self.connect:
            return self.cursor.execute("UPDATE users SET date_buy=(?) WHERE user_id=(?)", (30 ,user_id))
        
    async def add_sub_3month(self, user_id):
        with self.connect:
            return self.cursor.execute("UPDATE users SET date_buy=(?) WHERE user_id=(?)", (90 ,user_id))
        
    async def insert_sub(self, date):
        with self.connect:
            return self.cursor.execute("INSERT INTO users (date_buy) VALUES (?)", (date.strftime("%Y-%m-%d %H:%M:%S")))