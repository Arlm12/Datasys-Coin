import socket
import threading
import json
from collections import deque

class PoolServer:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.submitted_transactions = []  # Queue to hold submitted transactions
        self.unconfirmed_transactions = deque()  # Queue to hold unconfirmed transactions

    def start(self):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((self.host, self.port))
        self.server.listen()

        print(f"Pool Server listening on {self.host}:{self.port}")

        while True:
            client_socket, _ = self.server.accept()
            threading.Thread(target=self.handle_client, args=(client_socket,)).start()

    def handle_client(self, client_socket):
        while True:
            data = client_socket.recv(1024)
            if not data:
                break

            received_data = json.loads(data.decode('utf-8'))

            if received_data['type'] == 'submit':
                transaction_id = received_data['transaction']['id']
                acknowledgment_message = f"Transaction {transaction_id} received and added to 'submitted' pile"
                client_socket.send(acknowledgment_message.encode('utf-8'))
                self.submitted_transactions.append(received_data['transaction'])
                print(f"Received submitted transaction: {received_data['transaction']}")

            elif received_data['type'] == 'validator_request':
                if self.submitted_transactions:
                    last_transaction = self.submitted_transactions[-1]
                    self.unconfirmed_transactions.append(last_transaction)
                    del self.submitted_transactions[-1]
                    print(f"Moved transaction to 'unconfirmed': {last_transaction}")
                    client_socket.send(json.dumps(last_transaction).encode('utf-8'))
                else:
                    client_socket.send("No transaction available for validation".encode('utf-8'))

            elif received_data['type'] == 'remove_transaction':
                transaction_to_remove = received_data['transaction']
                if transaction_to_remove in self.unconfirmed_transactions:
                    self.unconfirmed_transactions.remove(transaction_to_remove)
                    client_socket.send("Transaction removed from pool".encode('utf-8'))
                else:
                    client_socket.send("Transaction not found in unconfirmed transactions".encode('utf-8'))


            elif received_data['type'] == 'get_status':
                if not self.submitted_transactions and not self.unconfirmed_transactions:
                    client_socket.send("Empty pool".encode('utf-8'))
                else:
                    transaction_id = received_data['transaction_id']
                    found = False

                    for transaction in self.submitted_transactions:
                        if transaction['transaction_id'] == transaction_id:
                            client_socket.send(json.dumps(transaction).encode('utf-8'))
                            found = True
                            break

                    for transaction in self.unconfirmed_transactions:
                        if transaction['transaction_id'] == transaction_id:
                            client_socket.send(json.dumps(transaction).encode('utf-8'))
                            found = True
                            break

                    if not found:
                        client_socket.send("Transaction not found in submitted or unconfirmed transactions".encode('utf-8'))

        client_socket.close()

if __name__ == "__main__":
    pool_server = PoolServer('127.0.0.1', 8888)
    pool_server.start()
