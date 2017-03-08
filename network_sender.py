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
			s.send(msg.encode())
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
			s.send(msg.encode())
			raw = recv_timeout_petlib_pack(s, timeout=0.1)
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
			s.send(msg.encode())
			raw = s.recv(1024)
			data = raw.decode()
			s.close()
			return data
		finally:
			self.lock.release()
