import sqlite3



class DatabaseManager:
    def __init__(self, db_name="payment_splitter"):
        self.db_name = db_name
        self.init_db()


    def get_connections(self):
        """returns connection context manager with FK enables"""
        conn = sqlite3.connect(self.db_name)
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn


    def init_db(self):
        """initalize tables if they do not exist"""
        with self.get_connections() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS members(id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT UNIQUE NOT NULL)""")

            cursor.execute("""CREATE TABLE IF NOT EXISTS expenses(id INTEGER PRIMARY KEY AUTOINCREMENT, description TEXT NOT NULL, amount REAL NOT NULL, payer_id INTEGER NOT NULL, FOREIGN KEY (payer_id) REFERENCES members(id) ON DELETE CASCADE)""")
