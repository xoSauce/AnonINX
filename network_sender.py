import socket		

class NetworkSender():
	def __init__(self):
		pass
	def send_data(self, msg, destination):
		ip = destination['ip']
		port = destination['port']
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.connect((ip, port))
		print (msg)
		s.send(msg.encode())
		data = s.recv(1024).decode()
		s.close()
		return data
