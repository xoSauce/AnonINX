from sphinxmix.SphinxParams import SphinxParams	
from sphinxmix.SphinxNode import sphinx_process

from epspvt_utils import getIp, RequestType
from network_sender import NetworkSender

class MixNode():

	def __init__(self, broker_config):
		self.private_key = None
		self.public_key = None
		self.ip = None
		self.params = SphinxParams()
		self.network_sender = NetworkSender()
		self.broker_config = broker_config

	def publish_key(self):

		def prepare_sending_pk(public_key, server_config):
			ip = server_config['pkserver']
			file = server_config['file']
			port = server_config['port']
			try:
				response = os.system("ping -c 1 " + ip)
				if response != 0:
					raise ValueError("Server: {} cannot be reached. The key was not published".format(ip))
				else:
					import json
					### This is how to retreive back the EC2Point export
					# debug_data = hexlify(public_key[2].export()).decode('utf-8')
					# print (public_key[2].export())
					# print (unhexlify(debug_data.encode()))
					###
					public_key_in_utf8 = {
						'type': RequestType.publish_data.value,
						'payload': {
							'id': hexlify(public_key[0]).decode('utf-8'),
							'pk': hexlify(public_key[2].export()).decode('utf-8')
						}
					}
					data_string = json.dumps(public_key_in_utf8)
					return (data_string, {'ip':ip, 'port':int(port), 'file_path': file})
			except Exception as error:
				print("Unexpected error: {}".format(error))
				return None
			return None

		json_data, destination = prepare_sending_pk(self.getPublicKey(), vars(broker_config))
		response = network_sender.send_pk(json_data, destination)
		print response
		
	def getPrivateKey(self):
		return self.private_key

	def getPublicKey(self):
		return self.public_key
	
	def getIp(self):
		if ip is None:
			self.ip = getIp()
		else:
			return self.ip

	def keyGenerate(self, params):
		#This getIp() potentially needs to be reworked
		ip = self.getIp()
		nid = Nenc(self.params, bytes(ip, 'utf8'))
		x = params.group.gensecret()
		y = params.group.expon(params.group.g, x)
		private_key = pki_entry(nid, x, y)
		public_key = pki_entry(nid, None, y)
		self.private_key = private_key
		self.public_key = public_key

	def send(self, header, delta, cb = None):
		private_key = self.getPrivateKey()
		ret = sphinx_process(self.params, self.getPrivateKey(), header, delta)
		(tag, info, (header, delta)) = ret
		routing = PFdecode(self.params, info)
		pass

Mix.run('aa','aa', 'aa')