import socket
import json
from generic_listener import GenericListener
from request_creator import RequestType
from mix import MixNode
from threading import Thread
from petlib.ec import EcPt
from binascii import unhexlify
from epspvt_utils import getGlobalSphinxParams
from logger import *
from socket_utils import recv_timeout
from request_creator import RequestCreator
from network_sender import NetworkSender
from sphinxmix.SphinxClient import Relay_flag, Dest_flag, Surb_flag
from broker_communicator import BrokerCommunicator
from epspvt_utils import Debug
from petlib.pack import encode
import pickle
class Worker(Thread):
	def __init__(self, socket, mixnode, mix_port):
		Thread.__init__(self)
		self.sock = socket
		self.mixnode = mixnode
		self.mix_port = mix_port
		self.network_sender = NetworkSender()
		self.start()

	def run(self):
		raw_data = recv_timeout(self.sock)
		data = pickle.loads(raw_data)
		if data['type'] == RequestType.push_to_mix.value:
			data = decode(data['payload'])
			header = data['header']
			delta = data['delta']
			result = self.mixnode.process(header, delta)
			if result[0] == Relay_flag:
				flag, addr, header, delta = result
				json_data, dest = RequestCreator().post_msg_to_mix(
					{'ip': addr, 'port': self.mix_port},
					{'header': header, 'delta': delta}
				)
				##TODO: POOL AT EVREY STEP !!
				self.mixnode.pool_item((json_data, dest))
				# self.network_sender.send_data(json_data, dest)
			elif result[0] == Dest_flag:
				flag, msg, dest, _ = result
				json_data, dest = RequestCreator().post_msg_to_db(dest, msg)
				# self.mixnode.pool_item((json_data, dest))
				# if Debug.dbg:
				# 	dest['ip'] = '0.0.0.0'
				self.network_sender.send_data(json_data, dest)
			elif result[0] == Surb_flag:
				flag, dest, myid, delta = result
				msg = {'myid': myid, 'delta': delta}
				self.mixnode.client_cache.setdefault(myid, []).append(msg)
		elif data['type'] == RequestType.client_poll.value:
			client_id = unhexlify(data['id'])
			if client_id in self.mixnode.client_cache:
				response = self.mixnode.client_cache.get(client_id)
				response = encode({"id": client_id, "response": response})
				self.sock.send(response)
				self.mixnode.client_cache.pop(client_id)
			else:
				self.sock.close()



class MixNodeListener(GenericListener):
	def __init__(self, port, mixnode):
		super().__init__(port)
		self.mixnode = mixnode

	def run(self):
		super().run()
		try:
			while 1:
				clientsocket, address = self.serversocket.accept()
				Worker(clientsocket, self.mixnode, self.port)
		finally:
			self.serversocket.close()
