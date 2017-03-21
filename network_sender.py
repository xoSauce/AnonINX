import socket
import threading
from socket_utils import recv_timeout_petlib_pack, recv_timeout
from PirSocket import PIRSocket
class NetworkSender():
	def __init__(self):
		self.lock = threading.Lock()

	def send_data(self, msg, destination):
		self.lock.acquire()
		try:
			ip = destination['ip']
			port = destination['port']
			s = PIRSocket()
			s.connect((ip, port))
			if type(msg).__name__ == 'str':
				msg = msg.encode()
			s.sendall(msg)
			s.close()
		finally:
			self.lock.release()

	# def send_data_wait_long_response(self, msg, destination):
	# 	self.lock.acquire()
	# 	try:
	# 		ip = destination['ip']
	# 		port = destination['port']
	# 		s = PIRSocket()
	# 		s.connect((ip, port))
	# 		if type(msg).__name__ == 'str':
	# 			msg = msg.encode()
	# 		s.sendall(msg)
	# 		raw = recv_timeout_petlib_pack(s)
	# 		data = raw
	# 		s.close()
	# 		return data
	# 	finally:
	# 		self.lock.release()

	def send_data_wait(self, msg, destination, timeout = None):
		self.lock.acquire()
		try:
			ip = destination['ip']
			port = destination['port']
			s = PIRSocket()
			s.connect((ip, port))
			if type(msg).__name__ == 'str':
				msg = msg.encode()
			s.sendall(msg)
			raw = recv_timeout(s, timeout=timeout)
			s.close()
			return raw
		finally:
			self.lock.release()
