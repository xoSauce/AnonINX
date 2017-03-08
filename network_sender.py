import socket
import threading
from socket_utils import recv_timeout_petlib_pack
class NetworkSender():
	def __init__(self):
		self.lock = threading.Lock()

	def send_data(self, msg, destination):
		self.lock.acquire()
		try:
			ip = destination['ip']
			port = destination['port']
			s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			s.connect((ip, port))
			if type(msg).__name__ == 'str':
				msg = msg.encode()
			print(msg, type(msg))

			s.send(msg)
			s.close()
		finally:
			self.lock.release()

	def send_data_wait_long_response(self, msg, destination):
		self.lock.acquire()
		try:
			ip = destination['ip']
			port = destination['port']
			s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			s.connect((ip, port))
			if type(msg).__name__ == 'str':
				msg = msg.encode()
			print(msg, type(msg))
			s.send(msg)
			raw = recv_timeout_petlib_pack(s)
			data = raw
			s.close()
			return data
		finally:
			self.lock.release()

	def send_data_wait(self, msg, destination):
		self.lock.acquire()
		try:
			ip = destination['ip']
			port = destination['port']
			s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			s.connect((ip, port))
			if type(msg).__name__ == 'str':
				print("here")
				msg = msg.encode()
			s.send(msg)
			raw = s.recv(1024)
			data = raw.decode()
			s.close()
			return data
		finally:
			self.lock.release()
