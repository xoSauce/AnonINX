from epspvt_utils import getPublicIp, getGlobalSphinxParams
from network_sender import NetworkSender
from request_creator import RequestCreator
from encryptor import Encryptor
import os
class DbNode():
	def __init__(self, broker_config):
		self.private_key = None
		self.public_key = None
		self.ip = None
		self.params = getGlobalSphinxParams()
		self.network_sender = NetworkSender()
		self.broker_config = broker_config
		self.encryptor = Encryptor(self.params.group)

	def getIp(self):
		if self.ip is None:
			self.ip = getPublicIp()
		return self.ip
	
	def publish_key(self):
		def prepare_sending_pk(public_key, server_config):
			key_server_ip = server_config['pkserver']
			port = server_config['port']
			try:
				response = os.system("ping -c 1 " + key_server_ip)
				if response != 0:
					raise ValueError("Server: {} cannot be reached. The key was not published".format(ip))
				else:
					request_creator = RequestCreator()
					json_data, destination = request_creator.post_db_key_request(
						{'ip':key_server_ip, 'port':port},
						{'id':public_key[0], 'pk':public_key[2]}
					)
					return (json_data, destination)
			except Exception as error:
				print("Unexpected error: {}".format(error))
				return None
			return None

		self.public_key, self.private_key = self.encryptor.keyGenerate(self.getIp())
		json_data, destination = prepare_sending_pk(self.public_key, self.broker_config)
		#publish key
		response = self.network_sender.send_data_wait(json_data, destination)
		return response