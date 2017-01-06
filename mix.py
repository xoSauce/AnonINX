from sphinxmix.SphinxParams import SphinxParams	
from sphinxmix.SphinxNode import sphinx_process
from sphinxmix.SphinxClient import pki_entry, Nenc
from epspvt_utils import getIp
from network_sender import NetworkSender
from request_creator import RequestCreator
import sys
import os

class MixNode():

	def __init__(self, broker_config):
		self.private_key = None
		self.public_key = None
		self.ip = None
		self.params = SphinxParams()
		self.network_sender = NetworkSender()
		self.broker_config = broker_config

	def publish_key(self):

		def keyGenerate(params):
			#This getIp() potentially needs to be reworked
			ip = self.getIp()
			nid = Nenc(ip)
			x = params.group.gensecret()
			y = params.group.expon(params.group.g, x)
			private_key = pki_entry(nid, x, y)
			public_key = pki_entry(nid, None, y)
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
		json_data, destination = prepare_sending_pk(self.getPublicKey(), vars(self.broker_config))
		#publish key
		response = self.network_sender.send_data(json_data, destination)
		return response
		
	def getPrivateKey(self):
		return self.private_key

	def getPublicKey(self):
		return self.public_key
	
	def getIp(self):
		if self.ip is None:
			self.ip = getIp()
		else:
			return self.ip

	def process_mix(self, header, delta, cb = None):
		private_key = self.getPrivateKey()
		ret = sphinx_process(self.params, self.getPrivateKey(), header, delta)
		(tag, info, (header, delta)) = ret
		routing = PFdecode(self.params, info)
		if routing[0] == Relay_flag:
		    flag, addr = routing
		    print (addr)	 
		elif routing[0] == Dest_flag:
			#Used currently for testing
			if cb is not None:
				cb()
			#assert receive_forward(params, delta) == [dest, message]

