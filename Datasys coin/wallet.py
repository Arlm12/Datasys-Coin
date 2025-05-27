import argparse
import datetime
import hashlib
import base58
import yaml
import random
import socket
import json

class Transaction:
    def __init__(self, sender_address, recipient_address, value):
        self.sender_address = sender_address  # 32-byte sender public address
        self.recipient_address = recipient_address  # 32-byte recipient public address
        self.value = value  # 8-byte unsigned double
        self.timestamp = int(datetime.datetime.now().timestamp())  # 8-byte signed integer
        self.transaction_id = self.generate_transaction_id()  # 16-byte transaction ID
        self.signature = self.generate_signature()  # 32-byte signature
        

    def generate_transaction_id(self):
        # Generate a random 16-byte transaction ID (for example, using random bytes)
        return ''.join(random.choices('0123456789abcdef', k=32))

    def generate_signature(self):
        # Generate a random 32-byte hash for the signature
        return hashlib.sha256(str(random.getrandbits(256)).encode('utf-8')).hexdigest()

    def __str__(self):
        return f"Transaction Details:\nSender Address: {self.sender_address}\nRecipient Address: {self.recipient_address}\nValue: {self.value}\nTimestamp: {self.timestamp}\nTransaction ID: {self.transaction_id}\nSignature: {self.signature}"


class Wallet:
    def __init__(self):
        self.public_key = None
        self.private_key = None
        self.pool_server_host = '127.0.0.1'  # Pool server host
        self.pool_server_port = 8888  # Pool server port

    def create(self):
        if self.public_key or self.private_key:
            print("Wallet already exists at dsc-key.yaml, wallet create aborted")
            return

        self.private_key = hashlib.sha256(str(random.getrandbits(256)).encode('utf-8')).hexdigest()
        self.public_key = base58.b58encode(hashlib.sha256(self.private_key.encode('utf-8')).digest()).decode('utf-8')

        current_time = datetime.datetime.now().strftime("%Y%m%d %H:%M:%S.%f")
        print(f"{current_time} DSC v1.0")
        print(f"{current_time} DSC Public Address: {self.public_key}")
        print(f"{current_time} DSC Private Address: {self.private_key}")
        print(f"{current_time} DSC type of Private Address: {type(self.private_key)}")
        
        with open('dsc-config.yaml', 'w') as config_file:
            yaml.dump({'public_address': self.public_key}, config_file)

        with open('dsc-key.yaml', 'w') as key_file:
            yaml.dump({'private_address': self.private_key}, key_file)

    def key(self):
        try:
            with open('dsc-config.yaml', 'r') as config_file, open('dsc-key.yaml', 'r') as key_file:
                config_data = yaml.safe_load(config_file)
                key_data = yaml.safe_load(key_file)

                public_key = config_data.get('public_address')
                private_key = key_data.get('private_address')

                if public_key and private_key:
                    current_time = datetime.datetime.now().strftime("%Y%m%d %H:%M:%S.%f")
                    print(f"{current_time} DSC v1.0")
                    print(f"{current_time} DSC Public Address: {public_key}")
                    print(f"{current_time} DSC Private Address: {private_key}")
                else:
                    print(f"{current_time} Error in finding key information, ensure that dsc-config.yaml and dsc-key.yaml exist and that they contain the correct information. You may need to run './dsc wallet create'")
        except FileNotFoundError:
            print("Error: Key information not found. Run './dsc wallet create' to generate keys.")

    def balance(self):
        current_time = datetime.datetime.now().strftime("%Y%m%d %H:%M:%S.%f")
        print(f"{current_time} DSC v1.0")
        print(f"{current_time} DSC Wallet balance: 0.0 coins at block 0")

    def create_transaction(self, recipient_address, value):
        # Create a transaction object
        sender_address = self.public_key if self.public_key else "Default_Sender_Address"
        transaction = Transaction(sender_address, recipient_address, value)
        return transaction

    def send(self, transaction):
        # Simulating sending transaction to pool server
        transaction_data = {
            'type': 'submit',
            'transaction': {
                'sender_address': transaction.sender_address,
                'recipient_address': transaction.recipient_address,
                'value': transaction.value,
                'timestamp': transaction.timestamp,
                'transaction_id': transaction.transaction_id,
                'signature': transaction.signature,
                'id': transaction.transaction_id
            }
        }

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            client_socket.connect((self.pool_server_host, self.pool_server_port))
            client_socket.send(json.dumps(transaction_data).encode('utf-8'))

            # Receive acknowledgment from the pool server
            response = client_socket.recv(1024)
            print(response.decode('utf-8'))

        print("\nTransaction Details:")
        print(transaction)

    def transaction(self, transaction_id):
        # Sending a request to the pool server to check transaction status
        transaction_data = {
            'type': 'get_status',
            'transaction_id': transaction_id
        }

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            client_socket.connect((self.pool_server_host, self.pool_server_port))
            client_socket.send(json.dumps(transaction_data).encode('utf-8'))

            response = client_socket.recv(1024)
            print(response.decode('utf-8'))
def main():
    parser = argparse.ArgumentParser(description="DSC: DataSys Coin Blockchain v1.0")
    parser.add_argument('operation', choices=['help', 'create', 'key', 'balance', 'send', 'transaction'])
    parser.add_argument('args', nargs='*', help="Additional arguments for the operation")

    args = parser.parse_args()

    wallet = Wallet()

    if args.operation == 'help':
        print("Help menu for Wallet, supported commands:")
        print("./dsc wallet help")
        print("./dsc wallet create")
        print("./dsc wallet key")
        print("./dsc wallet balance")
        print("./dsc wallet send <amount> <address>")
        print("./dsc wallet transaction <ID>")
    elif args.operation == 'create':
        wallet.create()
    elif args.operation == 'key':
        wallet.key()
    elif args.operation == 'balance':
        wallet.balance()
    elif args.operation == 'send':
        if len(args.args) == 2:
            amount, address = args.args
            transaction = wallet.create_transaction(address, amount)
            wallet.send(transaction)
        else:
            print("Incorrect number of arguments. Usage: ./dsc wallet send <amount> <address>")
    elif args.operation == 'transaction':
        if len(args.args) == 1:
            transaction_id = args.args[0]
            wallet.transaction(transaction_id)
        else:
            print("Incorrect number of arguments. Usage: ./dsc wallet transaction <ID>")
    else:
        print("Invalid operation. Use './dsc wallet help' for available commands.")

if __name__ == "__main__":
    main()
