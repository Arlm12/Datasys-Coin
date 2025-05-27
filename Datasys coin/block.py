from util.util import hash256


class Block:
    def __init__(self, blockheight,version, timestamp, difficulty, previous_hash, transaction):
        self.blockheight = blockheight
        self.timestamp = timestamp
        self.nonce = 0
        self.previous_hash = previous_hash
        self.version = version
        self.transaction = transaction
        self.difficulty = difficulty
        self.hash = ' '
        self.calculate_hash()

    def calculate_hash(self):
        while (self.hash[0:4]) != '0000':
                self.hash= hash256((str(self.version) + self.previous_hash + str(self.timestamp) + str(self.nonce)).encode() ).hex()
                    
                self.nonce += 1
                print(f"mining started {self.nonce}", end ='\r')
        return self.hash 