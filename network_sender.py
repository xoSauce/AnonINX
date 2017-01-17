import socket		
import threading

class NetworkSender():
	def __init__(self):
		self.lock = threading.Lock()
	
	def send_data(self, msg, destination):
		self.lock.acquire()
		try:
			ip = destination['ip']
			port = destination['port']
			s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			print("FROM networkSender: ", ip, port)
			s.connect((ip, port))
			s.send(msg.encode())
			s.close()
		finally:
			self.lock.release()

	def send_data_wait(self, msg, destination):
		self.lock.acquire()
		try:
			ip = destination['ip']
			port = destination['port']
			s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			print("FROM networkSender: ", ip, port)
			s.connect((ip, port))
			s.send(msg.encode())
			data = s.recv(1024).decode()
			s.close()
			return data
		finally:
			self.lock.release()
