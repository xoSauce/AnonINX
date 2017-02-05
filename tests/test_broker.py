import sys, os
myPath = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, myPath + '/../')

from binascii import hexlify
from broker import Broker
from threading import Thread, Lock

def test_broker_single_register():
	broker = Broker()
	data = {'pk':hexlify(b'this is a test').decode('utf-8'),
			'id':hexlify(b'someID').decode('utf-8')}
	broker.register(data, 'mix')
	cache = broker.fetch([], 'mix')
	assert len(cache) == 1

def test_broker_multiple_register():
	broker = Broker()
	data = [
	{'pk':hexlify(b'this is a test').decode('utf-8'),
	'id':hexlify(b'someID1').decode('utf-8')},
	{'pk':hexlify(b'this is a test').decode('utf-8'),
	'id':hexlify(b'someID2').decode('utf-8')},
	{'pk':hexlify(b'this is a test').decode('utf-8'),
	'id':hexlify(b'someID3').decode('utf-8')},
	{'pk':hexlify(b'this is a test').decode('utf-8'),
	'id':hexlify(b'someID4').decode('utf-8')},
	{'pk':hexlify(b'this is a test').decode('utf-8'),
	'id':hexlify(b'someID5').decode('utf-8')}
	]
	for entry in data:
		broker.register(entry, 'mix')
	cache = broker.fetch([], 'mix')
	assert len(cache) == 5

def test_broker_multiple_register_multithreaded():
	class Client(Thread):
		def __init__(self, data, broker):
			Thread.__init__(self)
			self.broker = broker
			self.data = data
			self.start()

		def run(self):
			self.broker.register(self.data, 'mix')


	broker = Broker()
	data = [
	{'pk':hexlify(b'this is a test').decode('utf-8'),
	'id':hexlify(b'someID1').decode('utf-8')},
	{'pk':hexlify(b'this is a test').decode('utf-8'),
	'id':hexlify(b'someID2').decode('utf-8')},
	{'pk':hexlify(b'this is a test').decode('utf-8'),
	'id':hexlify(b'someID3').decode('utf-8')},
	{'pk':hexlify(b'this is a test').decode('utf-8'),
	'id':hexlify(b'someID4').decode('utf-8')},
	{'pk':hexlify(b'this is a test').decode('utf-8'),
	'id':hexlify(b'someID5').decode('utf-8')}
	]
	threads = []
	for entry in data:
		threads.append(Client(entry, broker))
	for t1 in threads:
		t1.join()
	
	cache = broker.fetch([], 'mix')
	assert len(cache) == 5