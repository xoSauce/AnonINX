import threading
from binascii import unhexlify

class Broker():
	def __init__(self):
		self.public_keys = {}
		self.lock = threading.Lock()

	def fetch(self, data):
		self.lock.acquire()
		try:
			if data == []:
				return self.get_cache()
			else:
				return dict([x for x in map(self.get_cache_entry, data)])
		finally:
			self.lock.release()

	def register(self, data):
		self.lock.acquire()
		try:
			public_key_name = 'pk'
			id_name = 'id'
			print(data)
			if public_key_name in data and id_name in data:
				data[id_name] = data[id_name]
				self.public_keys.update({data[id_name]:data[public_key_name]}) 
		finally:
			self.lock.release()
	
	def get_cache(self):
			return self.public_keys

	def get_cache_entry(self, data):
		if data['id'] in public_keys:
			return (data['id'], public_keys[data['id']])
		else:
			raise ValueError('Requested id: %s was not made public' % data['id'])

	def dump():
		pass