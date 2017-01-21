import argparse
import json
from os import urandom
from binascii import hexlify, unhexlify
from sphinxmix.SphinxClient import pki_entry, Nenc
from sphinxmix.SphinxClient import rand_subset, create_forward_message
from request_creator import RequestCreator
from network_sender import NetworkSender
from epspvt_utils import getGlobalSphinxParams, Debug
from petlib.ec import EcPt
from logger import *
from broker_communicator import BrokerCommunicator
from encryptor import Encryptor

class Client:
	def __init__(self, public_key_server):
		self.broker_comm = BrokerCommunicator()
		self.network_sender = NetworkSender()
		self.public_key_server = public_key_server
		self.db_list = None
		self.mixnode_list = None
	
	def populate_broker_lists(self, source=None):
		if source == None:
			source = self.public_key_server

		def unhexlify_values(a_dict):
			for x in a_dict.keys():
				a_dict[x] = unhexlify(a_dict[x])
			return a_dict

		def get_db_list(source, client):
			dbs_dict_raw = client.broker_comm.getDBList({
					'ip': source['ip'],
					'port': source['port']
			})
			dbs_dict_raw = unhexlify_values(dbs_dict_raw)
			dbs_dict = {}
			for index, (key,value) in enumerate(dbs_dict_raw.items()):
				dbs_dict['DB{}'.format(index)] = (key, value)
			return dbs_dict

		def get_mixnode_list(source, client):
			mixnodes_dict = client.broker_comm.getMixNodeList({
					'ip': source['ip'],
					'port': source['port']
			})
			mixnodes_dict = unhexlify_values(mixnodes_dict)
			return mixnodes_dict

		self.mixnode_list = get_mixnode_list(source, self)
		self.db_list = get_db_list(source, self)

	def create_message(self, index):
		message = str(index).encode() 
		return hexlify(str(message).encode()) 

	def create_destination(self, destination):
		try:
			destination = self.db_list[destination]
			destination = (destination[0], EcPt.from_binary(destination[1], getGlobalSphinxParams().group.G))
			return destination
		except KeyError as e:
			raise 'Requested database not present or named incorrectly. {} not found'.format(destination)
	
	def request_data(self, index, db, mix_subset = 5, mix_port = 8081, session_name = None):
		if session_name == None:
			session_name = urandom(16)

		def json_encode(arguments):
			return json.dumps(dict(arguments))

		def prepare_forward_message(mixnodes_dict, message, dest):
			params = getGlobalSphinxParams()
			group = params.group.G	
			use_nodes = rand_subset(mixnodes_dict.keys(), 3)
			nodes_routing = list(map(Nenc, use_nodes))
			pks_chosen_nodes = [
				EcPt.from_binary(mixnodes_dict[key], group) 
				for key in use_nodes
			]
			header, delta =  create_forward_message(params, 
				nodes_routing, 
				pks_chosen_nodes, 
				dest, 
				message)
			return (header, delta, use_nodes[0])
		
		def preparePayload(index, dest, session_name):
			destination = self.create_destination(dest)
			group = getGlobalSphinxParams().group
			encryptor = Encryptor(group)
			g_x, iv, ciphertext, tag = encryptor.encrypt_aes_gcm(
				self.create_message(index)
				,destination[1]
				,session_name
			)
			e_message = {
				'pk': hexlify(g_x.export()).decode('utf-8')
				,'iv': hexlify(iv).decode('utf-8')
				,'text': hexlify(ciphertext).decode('utf-8')
				,'tag' : hexlify(tag).decode('utf-8')
			}
			print(e_message)
			json_msg = json.dumps(e_message, ensure_ascii=False)
			return (json_msg, dest)

		
		if len(self.mixnode_list) == 0:
			print("There are no mix-nodes available.")
			return

		if len(self.db_list) == 0:
			print("There are no databases available.")
			return
		e_message, dest = preparePayload(index, db, session_name)
		header, delta, first_mix = prepare_forward_message(self.mixnode_list,
			e_message,
			dest)
		json_data, dest = RequestCreator().post_msg_to_mix(
			{'ip': first_mix, 'port': mix_port},
			{'header': header, 'delta': delta}
		)
	
		if Debug.dbg is True:
			dest['ip'] = b'0.0.0.0'
		self.network_sender.send_data(json_data, dest)
		
def parse():
	parser = argparse.ArgumentParser()
	parser.add_argument('-d', '--debug', action= "store_true", help = "Debug Mode -- to be able to connect to own computer via local ip (skip public ip connection)")
	parser.add_argument('pkserver', help = "Specify the public IP address of the server where public keys will be stored.")
	parser.add_argument('port', help="Specify the port where the server is listening for connections")
	args = parser.parse_args()
	return args

def main():
	log_init("m_client.log")
	args = vars(parse())
	
	if args['debug']:
		Debug.dbg = True

	client = Client({
		'ip':args['pkserver'],
		'port': int(args['port'])
		})
	client.populate_broker_lists()
	client.request_data(1, 'DB0')

if __name__ == '__main__':
	main()