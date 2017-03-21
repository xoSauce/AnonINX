# from threading import Thread
# import threading
# from network_sender import NetworkSender
# from epspvt_utils import Debug
# import time
# class MixNodeSender(Thread):
# 	def print_pool(self):
# 		threading.Timer(5, self.print_pool).start()
# 		print ("POOL CONTENTS:", len(self.pool.getContents()))
#
# 	def __init__(self, pool):
# 		Thread.__init__(self)
# 		self.network_sender = NetworkSender()
# 		self.pool = pool
# 		self.print_pool()
#
# 	def run(self):
# 		while(1):
# 			items_to_send = self.pool.getSelection()
# 			for entry in items_to_send:
# 				json_data, destination = entry
# 				if Debug.dbg:
# 					destination['ip'] = '0.0.0.0'
# 				self.network_sender.send_data(json_data, destination)
# 			time.sleep(0.1)
