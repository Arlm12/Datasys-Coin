import socket
import json
import time
import hashlib
import os

from util.util import hash256

class Validator:
    def __init__(self, host, port, block_host, block_port):
        self.host = host
        self.port = port
        self.block_port = block_port
        self.block_host = block_host
        self.blockHash = '0'
        self.nonce = 0


    def request_last_transaction(self):
        ''' while (self.blockHash[0:4]) != '0000':
                
            random_string = os.urandom(16)  # Generate a 16-byte random string

            # Create a hash object using hashlib
            hash_object = hashlib.sha256(random_string)  # You can choose a different hash function (e.g., hashlib.sha512())

            # Get the hexadecimal representation of the hash
            self.blockHash = hash_object.hexdigest()

            self.nonce += 1'''

        while True:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as block_client:
                block_client.connect((self.block_host, self.block_port))

                request_data = {
                    'type': 'get_latest_block'
                }
                block_client.send(json.dumps(request_data).encode('utf-8'))

                response = block_client.recv(1024).decode('utf-8')
                last_block_data = json.loads(response)
                self.blockHash = last_block_data['hash']
                self.nonce = last_block_data['nonce']

            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
                client_socket.connect((self.host, self.port))

                request_data = {
                    'type': 'validator_request'
                }
                client_socket.send(json.dumps(request_data).encode('utf-8'))

                response = client_socket.recv(1024).decode('utf-8')

                if response == "No transaction available for validation":
                    print("No transaction found")
                else:
                    transaction = json.loads(response)
                    print(f"Received transaction to validate: {transaction}")
                    time.sleep(3)
                    print(f"Validating the transaction: {transaction}")

                    # Perform Proof of Work using sample block hash

                    nonce,block_hash,msg  = self.proof_of_work()  # Placeholder for PoW
                    time.sleep(1)
                    print(f"message {msg}")
                    print(f"block hash: {block_hash}")
                    print(f"Nonce: {nonce}")
                    print(f"Transaction validated with block hash: {block_hash}")
                    self.remove_transaction(transaction)

                time.sleep(0.1)  # Adjust the time interval for checking transactions

    def proof_of_work(self):
        nonce = 0
        msg = 'proof not found'
        target_bits = 1  # Number of bits to be zero in the hash
        target_bits = 30  # Number of leading zero bits
        target_bytes = target_bits // 8  # Convert bits to bytes (8 bits in a byte)
        target_hex_digits = target_bytes * 2
        print("running proof of work")
        print("fetching for the transaction")
        print("hash received")
        print(f"block_hash:{self.blockHash}")
        print(f"block_nonce: {self.nonce}")
        start_time = time.time()
        elapse = 0
        while elapse < 100:
            
            # Combine sample data and nonce
            data = f"{self.blockHash}{self.nonce}".encode('utf-8')

            # Hash the data (using SHA-256 in this example)
            guess = hashlib.sha256(data).hexdigest()

            # Check if the hash meets the target criteria (30 zero bits)
            if guess.startswith(self.blockHash[0:target_hex_digits]):
                msg = " proof found"
                return nonce, guess, msg  # Valid solution found
            #else:
            #   print("proof not found, failed programmer")

            nonce += 1  # Increment nonce and try again

            elapse = time.time() - start_time

        print(msg)
        return nonce,"",msg
    
    def fetch_latest_block(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            client_socket.connect((self.block_host, self.block_port))

            request_data = {
                'type': 'get_latest_block'
            }
            client_socket.send(json.dumps(request_data).encode('utf-8'))

            response = client_socket.recv(1024).decode('utf-8')
            block_data = json.loads(response)
            return block_data

    def remove_transaction(self, transaction):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            client_socket.connect((self.host, self.port))

            remove_data = {
                'type': 'remove_transaction',
                'transaction': transaction
            }
            client_socket.send(json.dumps(remove_data).encode('utf-8'))

            response = client_socket.recv(1024).decode('utf-8')
            if response == "Transaction removed from pool":
                print("Transaction removed from unconfirmed pool")
            else:
                print("Failed to remove transaction")

if __name__ == "__main__":
    validator = Validator('127.0.0.1', 8888, '127.0.0.1', 8891)
    validator.request_last_transaction()

