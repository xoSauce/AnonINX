from binascii import hexlify
from epspvt import server_key_publisher as skp
from threading import Thread, Lock

def test_broker_single_register():
	broker = skp.Broker()
	data = {'pk':hexlify('this is a test').decode('utf-8'),
			'id':hexlify('someID').decode('utf-8')}
	broker.register(data)
	cache = broker.get_cache()
	assert len(cache) == 1

def test_broker_multiple_register():
	broker = skp.Broker()
	data = [
	{'pk':hexlify('this is a test').decode('utf-8'),
	'id':hexlify('someID1').decode('utf-8')},
	{'pk':hexlify('this is a test').decode('utf-8'),
	'id':hexlify('someID2').decode('utf-8')},
	{'pk':hexlify('this is a test').decode('utf-8'),
	'id':hexlify('someID3').decode('utf-8')},
	{'pk':hexlify('this is a test').decode('utf-8'),
	'id':hexlify('someID4').decode('utf-8')},
	{'pk':hexlify('this is a test').decode('utf-8'),
	'id':hexlify('someID5').decode('utf-8')}
	]
	for entry in data:
		broker.register(entry)
	cache = broker.get_cache()
	assert len(cache) == 5

def test_broker_multiple_register_multithreaded():
	class Client(Thread):
		def __init__(self, data, broker):
			Thread.__init__(self)
			self.broker = broker
			self.data = data
			self.start()

		def run(self):
			print "here"
			self.broker.register(self.data)


	broker = skp.Broker()
	data = [
	{'pk':hexlify('this is a test').decode('utf-8'),
	'id':hexlify('someID1').decode('utf-8')},
	{'pk':hexlify('this is a test').decode('utf-8'),
	'id':hexlify('someID2').decode('utf-8')},
	{'pk':hexlify('this is a test').decode('utf-8'),
	'id':hexlify('someID3').decode('utf-8')},
	{'pk':hexlify('this is a test').decode('utf-8'),
	'id':hexlify('someID4').decode('utf-8')},
	{'pk':hexlify('this is a test').decode('utf-8'),
	'id':hexlify('someID5').decode('utf-8')}
	]
	threads = []
	for entry in data:
		threads.append(Client(entry, broker))
	for t1 in threads:
		t1.join()
	
	cache = broker.get_cache()
	assert len(cache) == 5