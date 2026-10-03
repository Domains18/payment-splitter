import sqlite3
from db.database import DatabaseManager
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


    def add_member(self, name: str, address: str):
        """registers a member alongside ther verified tron address"""
        name, address = name.strip(), address.strip()
        if not name or not address:
            raise ValueError("Name and tron address must be provided")
        if not address.startswith("T") or len(address) != 34:
            raise ValueError("Invalid Tron address format")

        try:
            with self.db.get_connections() as conn:
                conn.execute("INSERT INTO members (name, tron_address) VALUES(?, ?)", (name, address))
                conn.commit()
        except sqlite3.IntegrityError:
            raise ValueError("member already exists")


    def get_members(self):
        with self.db.get_connections() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM members")
            return cursor.fetchall()


    def get_main_wallet_usdt(self, private_key_hex: str) -> float:
        """fetches the current TRC-20 USDT balance of the primary signing wallet"""
        try:
            private_key = PrivateKey(bytes.fromhex(private_key_hex));
            main_address = private_key.public_key.to_base58check_address()

            contract = self.client.get_contract(USDT_CONTRACT)
            raw_balance = contract.functions.balanceOf(main_address)
            return float(raw_balance)/1_000_000
        except Exception as e:
            raise ValueError(f"failed to lookup balance in blockchain data: {str(e)}")


    def execute_blockchain_split(self, private_key_hex: str, total_usdt_to_split: float) -> list:
        """divides the requested usdt pool equally among wallets registered addresses, signs and executes the on chain transfer routines"""
        members = self.get_members()
        if not members:
            raise ValueError("no recepients in the database")

        number_recipients = len(members)
        share_per_person = total_usdt_to_split / number_recipients
        raw_share = int(share_per_person * 100_000)

        private_key = PrivateKey(bytes.fromhex(private_key_hex))
        sender_addr = private_key.public_key.to_base58check_address()
        contract = self.client.get_contract(USDT_CONTRACT)

        tx_receipts = []

        for name, address in members:
            try :
                txn = (contract.functions.transfer(address, raw_share)
                       .with_owner(sender_addr)
                       .fee_limit(20_000_000)
                       .build()
                    )

                txn.sign(private_key)
                result = txn.broadcast()

                tx_id = result.get('txid')
                with self.db.get_connections() as conn:
                    conn.execute("INSERT INTO payouts (tx_hash, amount_usdt) VALUES (?, ?)", (tx_id, share_per_person))
                    conn.commit()

                tx_receipts.append(f"sent {share_per_person:.2f} USDT to {name} -> Tx: {tx_id[:10]}...")
            except Exception as e:
                tx_receipts.append(f"failed to disburse to {name:} {str(e)}")

        return tx_receipts