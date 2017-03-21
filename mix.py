import sys
import os
import threading
import time
from sphinxmix.SphinxParams import SphinxParams
from sphinxmix.SphinxNode import sphinx_process
from sphinxmix.SphinxClient import PFdecode, Relay_flag, Dest_flag, Surb_flag, receive_forward
from epspvt_utils import getPublicIp, getGlobalSphinxParams, Debug
from network_sender import NetworkSender
from request_creator import RequestCreator
from encryptor import Encryptor
from broker_communicator import BrokerCommunicator
from binascii import unhexlify
from mix_pool import MixPool
from petlib.pack import encode
from datetime import datetime
import logger
class MixNode():

	def __init__(self, broker_config, pool_size=3):
		self.private_key = None
		self.public_key = None
		self.ip = None
		self.params = getGlobalSphinxParams()
		self.network_sender = NetworkSender()
		self.broker_config = broker_config
		self.encryptor = Encryptor(self.params.group)
		self.db_list = None
		self.broker_comm = BrokerCommunicator()
		self.client_cache = {}
		self.mix_pool = MixPool(pool_size)
		self.client_backlog = set()

	def handlePool(self, pool_lock):
		while(1):
			with pool_lock:
				print("POOL SIZE: {}".format(len(self.mix_pool.getContents())))
				items_to_send = self.mix_pool.getSelection()
			for entry in items_to_send:
				json_data, destination = entry
				if Debug.dbg:
					destination['ip'] = '0.0.0.0'
				self.network_sender.send_data(json_data, destination)
			time.sleep(0.05)

	def handleCache(self, backlog_lock):
		while 1:
			toRemove = []
			with backlog_lock:
				print('Cache size: {}'.format(len(self.client_cache)))
				for entry in self.client_backlog:
					client_id, socket = entry
					if client_id in self.client_cache:
						toRemove.append(entry)
						start = time.time()
						operation = ''
						response = self.client_cache.get(client_id)
						response = encode({"id": client_id, "response": response})
						socket.sendall(response)
						self.client_cache.pop(client_id)
						operation = '[CLIENT_POLL] send'
						end = time.time()
						timestamp = datetime.fromtimestamp(
							end - start).strftime('%M:%S:%f')
						logger.log_info(
							'[TIME] MIX LISTENER {} TOOK {}'.format(operation, timestamp))
				for entry in toRemove:
					self.client_backlog.remove(entry)
			time.sleep(0.05)

	def pool_item(self, item):
		self.mix_pool.addInPool(item)

	def getDbList(self):

		def unhexlify_values(a_dict):
			for x in a_dict.keys():
				a_dict[x] = unhexlify(a_dict[x])
			return a_dict

		def _get_db_list(source):
			dbs_dict_raw = self.broker_comm.getDBList({
				'ip': source['ip'],
				'port': source['port']
			})
			dbs_dict_raw = unhexlify_values(dbs_dict_raw)
			dbs_dict = {}
			for index, (key, value) in enumerate(dbs_dict_raw.items()):
				dbs_dict['DB{}'.format(index)] = (key, value)
			return dbs_dict

		if self.db_list == None:
			source = {
				'ip': self.broker_config['pkserver'],
				'port': self.broker_config['port']
			}
			self.db_list = _get_db_list(source)
		return self.db_list

	def publish_key(self):

		def prepare_sending_pk(public_key, server_config):
			key_server_ip = server_config['pkserver']
			port = server_config['port']
			try:
				response = os.system("ping -c 1 " + key_server_ip)
				if response != 0:
					raise ValueError(
						"Server: {} cannot be reached. The key was not published".format(ip))
				else:
					request_creator = RequestCreator()
					json_data, destination = request_creator.post_mix_key_request(
						{'ip': key_server_ip, 'port': port},
						{'id': public_key[0], 'pk': public_key[2]}
					)
					return (json_data, destination)
			except Exception as error:
				print("Unexpected error: {}".format(error))
				return None
			return None

		self.public_key, self.private_key = self.encryptor.keyGenerate(
			self.getIp())
		json_data, destination = prepare_sending_pk(
			self.public_key, self.broker_config)
		# publish key
		response = self.network_sender.send_data(json_data, destination)
		return response

	def getIp(self):
		if self.ip is None:
			self.ip = getPublicIp()
		return self.ip

	def process(self, header, delta, cb=None):
		private_key = self.private_key
		ret = sphinx_process(self.params, private_key.x, header, delta)
		(tag, info, (header, delta)) = ret
		routing = PFdecode(self.params, info)
		if routing[0] == Relay_flag:
			flag, addr = routing
			return (Relay_flag, addr, header, delta)
		elif routing[0] == Dest_flag:
			dest, msg = receive_forward(self.params, delta)
			return (Dest_flag, msg, dest, None)
		elif routing[0] == Surb_flag:
			flag, dest, myid = routing
			return (flag, dest, myid, delta)
