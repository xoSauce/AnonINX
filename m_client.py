import argparse
import json
from os import urandom
from binascii import hexlify, unhexlify
from sphinxmix.SphinxClient import pki_entry, Nenc
from sphinxmix.SphinxClient import rand_subset, create_forward_message, create_surb, receive_surb
from request_creator import RequestCreator, PortEnum, PortEnumDebug
from network_sender import NetworkSender
from epspvt_utils import getGlobalSphinxParams, Debug, getPublicIp
from petlib.ec import EcPt
from logger import *
from broker_communicator import BrokerCommunicator
from encryptor import Encryptor
from petlib.pack import encode,decode
from client_listener import ClientListener
from message_creator import MessageCreator
class Client:
	def __init__(self, public_key_server):
		self.broker_comm = BrokerCommunicator()
		self.public_key_server = public_key_server
		self.db_list = None
		self.mixnode_list = None
		self.ip = getPublicIp()
		self.encryptor = Encryptor(getGlobalSphinxParams().group)
		self.surbDict = {}

	def listen(self, requested_index, port):
		self.client_listener = ClientListener(port, self)
		self.client_listener.listen_for(requested_index)
	
	def recoverMessage(self, msg):
		surbkeytuple, index = self.surbDict[msg['myid']]
		return (index, decode(receive_surb(getGlobalSphinxParams(), surbkeytuple, msg['delta']))) 

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
				dbs_dict[index] = (key, value)
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

	def create_db_message(self, index, additional_data = None):
		msg = {
				'index': index,
				'additional_data': additional_data,
				'nymtuple': None
			}
		return msg

	def create_db_destination(self, destination, port):
		try:
			destination = self.db_list[destination]
			destination = (destination[0], destination[1], port)
			key = EcPt.from_binary(destination[1], getGlobalSphinxParams().group.G)
			return (destination, key)
		except Exception as e:
			raise Exception('Requested database not present or named incorrectly. {} not found'.format(destination))
	
	def package_message(self, index, db, pir_xor, portEnum, mix_subset = 5, session_name = None):

		self.public_key, self.private_key = self.encryptor.keyGenerate(session_name)
		self.session_name = session_name

		def json_encode(arguments):
			return json.dumps(dict(arguments))

		def prepareDBPayload(msg, key, session_name):
			group = getGlobalSphinxParams().group
			g_x, iv, ciphertext, tag = self.encryptor.encrypt_aes_gcm(
				msg
				,key
				,session_name
			)
			e_message = {
				'pk': hexlify(g_x.export()).decode('utf-8')
				,'iv': hexlify(iv).decode('utf-8')
				,'text': hexlify(ciphertext).decode('utf-8')
				,'tag' : hexlify(tag).decode('utf-8')
				,'pir_method': pir_xor
			}
			json_msg = json.dumps(e_message, ensure_ascii=False)
			return (json_msg)

		def prepare_forward_message(mixnodes_dict, message, dest, key, portEnum):
			params = getGlobalSphinxParams()
			group = params.group.G	
			use_nodes_forward = rand_subset(mixnodes_dict.keys(), 5)
			use_nodes_backward = rand_subset(mixnodes_dict.keys(), 5)
			nodes_routing_forward = list(map(Nenc, use_nodes_forward))
			nodes_routing_backward = list(map(Nenc, use_nodes_backward))
			pks_chosen_nodes_forward = [
				EcPt.from_binary(mixnodes_dict[key], group) 
				for key in use_nodes_forward
			]
			pks_chosen_nodes_backward = [
				EcPt.from_binary(mixnodes_dict[key], group) 
				for key in use_nodes_backward
			]
			surbid, surbkeytuple, nymtuple = create_surb(
				params, 
				nodes_routing_backward, 
				pks_chosen_nodes_backward, 
				self.ip)
			self.surbDict[surbid] = [surbkeytuple]
			message['nymtuple'] = nymtuple
			# message['pk'] = self.public_key
			message = encode(message)
			json_msg = prepareDBPayload(message, key, self.session_name)
			header, delta =  create_forward_message(params, 
				nodes_routing_forward, 
				pks_chosen_nodes_forward, 
				dest, 
				json_msg)
			return (header, delta, use_nodes_forward[0], surbid)
		
		if len(self.mixnode_list) == 0:
			print("There are no mix-nodes available.")
			return

		if len(self.db_list) == 0:
			print("There are no databases available.")
			return
		db_dest, key = self.create_db_destination(db, portEnum.db.value)
		message = self.create_db_message(index)
		header, delta, first_mix, surbid = prepare_forward_message(self.mixnode_list,
			message,
			db_dest,
			key,
			portEnum)
		self.surbDict[surbid].append(index)
		json_data, dest = RequestCreator().post_msg_to_mix(
			{'ip': first_mix, 'port': portEnum.mix.value},
			{'header': header, 'delta': delta}
		)
		if Debug.dbg is True:
			dest['ip'] = b'0.0.0.0'
		return (json_data, dest)
		
def parse():
	parser = argparse.ArgumentParser()
	parser.add_argument('-d', '--debug', action= "store_true", help = "Debug Mode -- to be able to connect to own computer via local ip (skip public ip connection)")
	parser.add_argument('-x', '--xor', action="store_true", help = "Use vector xoring method")
	parser.add_argument('pkserver', help = "Specify the public IP address of the server where public keys will be stored.")
	parser.add_argument('port', help="Specify the port where the server is listening for connections")
	parser.add_argument('-i', '--requested_index', help="Specify the index to retrieve")
	parser.add_argument('-db', '--database', help="Specify the number of the datbase in the range[0-?]")
	args = parser.parse_args()
	return args

def main():
	log_init("m_client.log")
	args = vars(parse())
	portEnum = PortEnum
	if args['debug']:
		Debug.dbg = True
		portEnum = PortEnumDebug

	client = Client({
		'ip':args['pkserver'],
		'port': portEnum.broker.value
		})
	client.populate_broker_lists()
	index = int(args['requested_index'])
	db = int(args['database'])
	requested_index, requested_db = (index, db)
	messageCreator = MessageCreator(client)

	if args['xor']:
		messages = messageCreator.generate_messages(requested_index, requested_db, 10, portEnum, pir_xor = True)
	else:
		messages = messageCreator.generate_messages(requested_index, requested_db, 10, portEnum, pir_xor = False)
	print(messages)
	network_sender = NetworkSender()
	for db in messages:
		[network_sender.send_data(json, dest) for json,dest in messages[db]]	
	client.listen(requested_index, portEnum.db)
	
if __name__ == '__main__':
	main()