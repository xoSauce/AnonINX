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
class Worker(Thread):
	def __init__(self, socket, mixnode, mix_port):
		Thread.__init__(self)
		self.sock = socket
		self.mixnode = mixnode
		self.mix_port = mix_port
		self.network_sender = NetworkSender()
		self.start()

	def run(self):
		def reconstruct_header(h_0, h_1, h_2):
			h_0 = unhexlify(h_0)
			params = getGlobalSphinxParams()
			group = params.group.G
			ecPt = EcPt.from_binary(h_0, group)
			return (ecPt, unhexlify(h_1), unhexlify(h_2))

		raw_data = recv_timeout(self.sock, timeout=1)
		data = json.loads(raw_data)
		if data['type'] == RequestType.push_to_mix.value:
			data = data['payload']
			header = reconstruct_header(data['header_0'], data['header_1'], data['header_2'])
			delta = unhexlify(data['delta'])
			log_debug(header)
			log_debug(delta)
			result = self.mixnode.process(header, delta)
			if result[0] == Relay_flag:
				flag, addr, header, delta = result
				json_data, dest = RequestCreator().post_msg_to_mix(
					{'ip': addr, 'port': self.mix_port},
					{'header': header, 'delta': delta}
				)
				self.network_sender.send_data(json_data, dest)
			elif result[0] == Dest_flag:
				flag, msg, dest, _ = result
				json_data, dest = RequestCreator().post_msg_to_db(dest, msg)
				if Debug.dbg:
					dest['ip'] = '0.0.0.0'
				self.network_sender.send_data(json_data, dest)
			elif result[0] == Surb_flag:
				flag, dest, myid = result
				msg = {'myid': myid, 'delta': delta}
				json_data, dest = RequestCreator().post_msg_to_client(dest, msg)
				if Debug.dbg:
					dest['ip'] = '0.0.0.0'
				self.network_sender.send_data(json_data, dest)
				print ("SURB: FLAG {} \n DEST {} \n MYID{} \n".format(flag,dest,myid))

class MixNodeListener(GenericListener):
	def __init__(self, port, mixnode):
		super().__init__(port)
		self.mixnode = mixnode
	
	def listen(self):
		super().listen()
		try:
			while 1:
				clientsocket, address = self.serversocket.accept()
				Worker(clientsocket, self.mixnode, self.port)
		finally:
			self.serversocket.close()