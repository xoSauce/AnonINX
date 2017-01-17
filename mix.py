import sys
import os
from sphinxmix.SphinxParams import SphinxParams	
from sphinxmix.SphinxNode import sphinx_process
from sphinxmix.SphinxClient import pki_entry, PFdecode, Relay_flag, Dest_flag, receive_forward
from epspvt_utils import getPublicIp, getGlobalSphinxParams
from network_sender import NetworkSender
from request_creator import RequestCreator

class MixNode():

	def __init__(self, broker_config):
		self.private_key = None
		self.public_key = None
		self.ip = None
		self.params = getGlobalSphinxParams()
		self.network_sender = NetworkSender()
		self.broker_config = broker_config

	def publish_key(self):

		def keyGenerate(params):
			#This getIp() potentially needs to be reworked
			ip = self.getIp().encode()
			x = params.group.gensecret()
			y = params.group.expon(params.group.g, x)
			private_key = pki_entry(ip, x, y)
			public_key = pki_entry(ip, None, y)
			self.private_key = private_key
			self.public_key = public_key

		def prepare_sending_pk(public_key, server_config):
			key_server_ip = server_config['pkserver']
			file = server_config['file']
			port = server_config['port']
			try:
				response = os.system("ping -c 1 " + key_server_ip)
				if response != 0:
					raise ValueError("Server: {} cannot be reached. The key was not published".format(ip))
				else:
					request_creator = RequestCreator()
					json_data, destination = request_creator.post_key_request(
						{'ip':key_server_ip, 'port':port},
						{'id':public_key[0], 'pk':public_key[2]}
					)
					return (json_data, destination)
			except Exception as error:
				print("Unexpected error: {}".format(error))
				return None
			return None

		keyGenerate(self.params)
		json_data, destination = prepare_sending_pk(self.getPublicKey(), self.broker_config)
		#publish key
		response = self.network_sender.send_data_wait(json_data, destination)
		return response
		
	def getPrivateKey(self):
		return self.private_key

	def getPublicKey(self):
		return self.public_key
	
	def getIp(self):
		if self.ip is None:
			self.ip = getPublicIp()
		return self.ip

	def process(self, header, delta, cb = None):
		private_key = self.getPrivateKey()
		ret = sphinx_process(self.params, self.getPrivateKey().x, header, delta)
		(tag, info, (header, delta)) = ret
		routing = PFdecode(self.params, info)
		print(routing)
		if routing[0] == Relay_flag:
			flag, addr = routing
			return (Relay_flag, addr, header, delta)
		elif routing[0] == Dest_flag:
			msg, dest = receive_forward(self.params, delta)
			return (Dest_flag, msg, dest, None)
			#Used currently for testing
			if cb is not None:
				cb()
