import argparse
import json
from binascii import unhexlify
from sphinxmix.SphinxClient import pki_entry, Nenc
from sphinxmix.SphinxClient import rand_subset, create_forward_message
from request_creator import RequestCreator
from network_sender import NetworkSender
from epspvt_utils import getGlobalSphinxParams, Debug
from petlib.ec import EcPt

class Client:
	def __init__(self, public_key_server):
		self.network_sender = NetworkSender()
		self.public_key_server = public_key_server
	
	def getList(self, source):
		request_creator = RequestCreator()
		data_string, serialized_destination = request_creator.get_all_mixnode_request(source)
		response = self.network_sender.send_data(data_string, serialized_destination)
		return json.loads(response)

	def fetch_data(self, index, mix_subset = 5, mix_port = 8081):
		def unhexlify_keys(a_dict):
			new_dict = {}
			for x in a_dict.keys():
				new_dict[unhexlify(x)] = a_dict[x]
			return new_dict

		def unhexlify_values(a_dict):
			for x in a_dict.keys():
				a_dict[x] = unhexlify(a_dict[x])
			return a_dict

		def json_encode(arguments):
			return json.dumps(dict(arguments))

		def prepare_forward_message(mixnodes_dict, message, dest):
			params = getGlobalSphinxParams()
			group = params.group.G	
			mixnodes_dict = unhexlify_keys(mixnodes_dict)
			mixnodes_dict = unhexlify_values(mixnodes_dict)
			use_nodes = rand_subset(mixnodes_dict.keys(), 5)
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
		
		mixnodes_dict = self.getList({
				'ip': self.public_key_server['ip'],
				'port': self.public_key_server['port']
		})

		message = b'This is a test'
		dest = b'Bob'

		header, delta, first_mix = prepare_forward_message(mixnodes_dict,
			message,
			dest)
		json_data, dest = RequestCreator().post_msg_to_mix(
			{'ip': first_mix, 'port': mix_port},
			{'header': header, 'delta': delta}
		)
	
		if Debug.dbg is True:
			dest['ip'] = b'0.0.0.0'

		print(dest)
		self.network_sender.send_data(json_data, dest)
		
		

def parse():
	parser = argparse.ArgumentParser()
	parser.add_argument('-f', '--file', help = "The IP address will be stored in this file. Alternatively a default file will be provided.")
	parser.add_argument('-d', '--debug', action= "store_true", help = "Debug Mode -- to be able to connect to own computer via local ip (skip public ip connection)")
	parser.add_argument('pkserver', help = "Specify the public IP address of the server where public keys will be stored.")
	parser.add_argument('port', help="Specify the port where the server is listening for connections")
	args = parser.parse_args()
	print (args)
	return args

def main():
	args = vars(parse())
	
	if args['debug']:
		Debug.dbg = True

	client = Client({
		'ip':args['pkserver'],
		'port': args['port']
		})
	client.fetch_data(1)

if __name__ == '__main__':
	main()