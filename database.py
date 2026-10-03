import sqlite3



class DatabaseManager:
    def __init__(self, db_name="trc20_splitter.db"):
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
            CREATE TABLE IF NOT EXISTS members(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            tron_address TEXT UNIQUE NOT NULL
            )""")

            """store executed batchj distribution payouts for audit"""
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS payouts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tx_hash TEXT UNIQUE NOT NULL,
                    amount_usdt REAL NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)

            conn.commit()
