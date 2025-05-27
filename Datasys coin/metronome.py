
import random
import socket
import json
import time
from block import Block
from blockchain_test import BlockchainServer

#from util.util import hash256

'''class Block:
    def __init__(self, blockheight,version, timestamp, previous_hash, transaction):
        self.blockheight = blockheight
        self.timestamp = timestamp
        self.nonce = 0
        self.previous_hash = previous_hash
        self.version = version
        self.transaction = transaction
        self.hash = ' '
        self.calculate_hash()

    def calculate_hash(self):
        while (self.hash[0:4]) != '0000':
                self.hash= hash256((str(self.version) + self.previous_hash + str(self.timestamp) + str(self.nonce)).encode() ).hex()
                    
                self.nonce += 1
                print(f"mining started {self.nonce}", end ='\r')
        return self.hash 
'''

class Metronome:
    def __init__(self, blockchain_host, blockchain_port):
        self.blockchain_host = blockchain_host
        self.blockchain_port = blockchain_port
        BlockchainServer.blockchain = [self.create_genesis_block()]
        self.difficulty = 0

    def create_genesis_block(self):
        # Create the first block (genesis block)
        return Block(0 , 1, time.time(), 4, "0" * 64, "Genesis Block")
    
    def add_block(self, new_block):
        new_block.blockheight = len(BlockchainServer.blockchain)
        new_block.previous_hash = BlockchainServer.blockchain[-1].hash
        new_block.hash = new_block.calculate_hash()
        BlockchainServer.blockchain.append(new_block)

    def send_empty_block(self):

        #random_hash = ''.join(random.choices('0123456789abcdef', k=64))
        transaction = "0"
        self.difficulty = BlockchainServer.blockchain[-1].difficulty
        new_block = Block(BlockchainServer.blockchain[-1].blockheight,1, time.time(), self.difficulty, BlockchainServer.blockchain[-1].hash, transaction)

        # Add the block to the blockchain
        self.add_block(new_block)

        print(f"Block {len(BlockchainServer.blockchain) - 1} added to the blockchain:")
        print(json.dumps(new_block.__dict__, indent=4))
       

        metronome_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        metronome_socket.connect((self.blockchain_host, self.blockchain_port))

        metronome_socket.send(json.dumps(new_block.__dict__).encode('utf-8'))
        print("Empty block signal sent to the Blockchain")

        response = metronome_socket.recv(1024).decode('utf-8')
        print(f"Response from Blockchain: {response}")

        metronome_socket.close()

if __name__ == "__main__":
    blockchain_host = '127.0.0.1'  # Update with the Blockchain server's IP
    blockchain_port = 8891  # Update with the Blockchain server's port

    metronome = Metronome(blockchain_host, blockchain_port)
    metronome_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    metronome_socket.connect((blockchain_host, blockchain_port))

    metronome_socket.send(json.dumps(BlockchainServer.blockchain[0].__dict__).encode('utf-8'))
    print("Empty block signal sent to the Blockchain")

    response = metronome_socket.recv(1024).decode('utf-8')
    print(f"Response from Blockchain: {response}")

    metronome_socket.close()
    time.sleep(6)


    # Send an empty block every 10 seconds (adjust as needed)
    while True:
        metronome.send_empty_block()
        time.sleep(6)
