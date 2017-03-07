import time
import random
import threading
class MixPool:
	def __init__(self, min_pool_size):
		self.min_size = min_pool_size
		self.pool = []
		self.SLEEP_TIME = 0.5
		self.lock = threading.Lock()

	def getSelection(self, selection_size = None):
		self.lock.acquire()
		try:
			if selection_size is None:
				selection_size = self.min_size

			while(len(self.pool) - selection_size < self.min_size):
				time.sleep(self.SLEEP_TIME)

			secure_random = random.SystemRandom()
			secure_random.shuffle(self.pool)
			result = self.pool[(selection_size*(-1)):]
			self.pool = self.pool[:(selection_size*(-1))]
			return result
		finally:
			self.lock.release()

	def addInPool(self, item):
		self.pool.append(item)

