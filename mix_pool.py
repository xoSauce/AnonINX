import random
class MixPool:
    def __init__(self, min_pool_size):
        self.min_size = min_pool_size
        self.pool = []
        self.SLEEP_TIME = 0.5

    def getContents(self):
        return self.pool

    ### Selecting packets out of the pool such that the property of holding
    ### at least min_size packets is mantained.
    def getSelection(self):
        selection_size = min(self.min_size, len(self.pool) - self.min_size)
        if selection_size > 0:
            secure_random = random.SystemRandom()
            secure_random.shuffle(self.pool)
            result = self.pool[(selection_size*(-1)):]
            self.pool = self.pool[:(selection_size*(-1))]
            return result
        return []

    def addInPool(self, item):
        self.pool.append(item)
