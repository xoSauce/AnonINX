from threading import Thread
from network_sender import NetworkSender
from epspvt_utils import Debug

class MixNodeSender(Thread):
	def __init__(self, pool):
		Thread.__init__(self)
		self.network_sender = NetworkSender()
		self.pool = pool
		
	def run(self):
		while(1):
			print("here")
			items_to_send = self.pool.getSelection()
			print(items_to_send)
			for entry in items_to_send:
				json_data, destination = entry
				print(destination)
				if Debug.dbg:
					destination['ip'] = '0.0.0.0'
				self.network_sender.send_data(json_data, destination)
