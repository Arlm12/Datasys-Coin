import socket
import json
import threading

class BlockchainServer:
    def __init__(self):
        self.host = '127.0.0.1'
        self.port = 8891
        self.blockchain = []  # Blockchain data

    def get_latest_block(self):
        if self.blockchain:
            return self.blockchain[-1]  # Return the most recent block
        else:
            return {"message": "No blocks exist"}  # Indicate no blocks exist

    def start_server(self):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((self.host, self.port))
        server_socket.listen(5)
        print(f"Blockchain server listening on port {self.port}...")

        while True:
            client_socket, addr = server_socket.accept()
            print(f"Connection established with {addr}")

            request_data = client_socket.recv(1024).decode('utf-8')
            if request_data:
                block_data = json.loads(request_data)
                if 'blockheight' in block_data:
                    if not self.blockchain and block_data['blockheight'] == 0:
                        print("Received genesis block signal from Metronome")
                        self.blockchain.append(block_data)
                        print("Genesis block added to the blockchain:")
                        print(json.dumps(block_data, indent=4))  # Display received block data
                        client_socket.send("Genesis block received by the Blockchain".encode('utf-8'))
                    elif block_data['transaction'] == 'empty transactions':
                        print("Received empty block signal from Metronome")
                        # Process the empty block (for demonstration, add to blockchain list)
                        self.blockchain.append(block_data)
                        print("Empty block added to the blockchain:")
                        print(json.dumps(block_data, indent=4))  # Display received block data
                        client_socket.send("Empty block received by the Blockchain".encode('utf-8'))
                    else:
                        print("Invalid block data received")
                        client_socket.send("Invalid block data".encode('utf-8'))
                elif block_data['type'] == 'get_latest_block':
                    latest_block = self.get_latest_block()
                    response = json.dumps(latest_block)
                    client_socket.send(response.encode('utf-8'))
                else:
                    print("Invalid request type")
                    client_socket.send("Invalid request".encode('utf-8'))

            client_socket.close()

if __name__ == "__main__":
    blockchain_server = BlockchainServer()
    server_thread = threading.Thread(target=blockchain_server.start_server)
    server_thread.start()
