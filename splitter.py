import sqlite3
from database import DatabaseManager
from tronpy import Tron
from tronpy.keys import PrivateKey
import os

#s
USDT_CONTRACT = os.getenv('USDT_CONTRACT', 'USDT_CONTRACT = "TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t')

class SplitterEngine:
    def __init__(self, db_manager: DatabaseManager, use_testnet = True) -> None:
        self.db = db_manager
        if use_testnet:
            self.client = Tron(network='shasta')
        else:
            self.client = Tron()