import threading
from binascii import unhexlify

class Broker():
	def __init__(self):
		self.public_keys = {}
		self.lock = threading.Lock()

	def register(self, data):
		self.lock.acquire()
		try:
			public_key_name = 'pk'
			id_name = 'id'
			if public_key_name in data and id_name in data:
				data[id_name] = unhexlify(data[id_name])
				self.public_keys.update({data[id_name]:data[public_key_name]}) 
		finally:
			self.lock.release()
	
	def get_cache(self):
		self.lock.acquire()
		try:
			return self.public_keys
		finally:
			self.lock.release()

	def get_cache_entry(self, data):
		self.lock.acquire()
		try:
			if data['id'] in public_keys:
				return public_keys[data['id']]
			else:
				raise ValueError('Requested id was not made public')
		finally:
			self.lock.release()

	def dump():
		pass