import sphinxmix
from sphinxmix.SphinxParams import SphinxParams

# The minimal PKI involves names of nodes and keys
from sphinxmix.SphinxNode import Nenc
from sphinxmix.SphinxClient import pki_entry
from epspvt_utils import getIp, RequestType
from binascii import hexlify, unhexlify
import sys
import argparse
import os

def send_pk(msg, destination):
	ip = destination['ip']
	port = destination['port']
	file = destination['file_path']
	import socket
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.connect((ip, port))
	print (msg)
	s.send(msg.encode())
	data = s.recv(1024).decode()
	s.close()
	return data

### Checks if the server is reachable and serializes data.
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

### Generates private and public keys
### Returns a tuple of public, private_key
def keyGen(params):
	#This getIp() potentially needs to be reworked
	ip = getIp()
	nid = Nenc(params, bytes(ip, 'utf8'))
	print (len(nid))
	x = params.group.gensecret()
	y = params.group.expon(params.group.g, x)
	private_key = pki_entry(nid, x, y)
	public_key = pki_entry(nid, None, y)
	return (public_key, private_key)

### Argument parsing function
### Returns a Namespace of arguments
def parse():
	parser = argparse.ArgumentParser()
	parser.add_argument('-f', '--file', help = "The IP address will be stored in this file. Alternatively a default file will be provided.")
	parser.add_argument('pkserver', help = "Specify the public IP address of the server where public keys will be stored.")
	parser.add_argument('port', help="Specify the port where the server is listening for connections")
	args = parser.parse_args()
	print (args)
	return args

def main():
	server_config = parse()
	params = SphinxParams(r = 5)
	public_key, private_key = keyGen(params)
	json_data, destination = prepare_sending_pk(public_key, vars(server_config))
	response = send_pk(json_data, destination)
	print (response)

if __name__ == '__main__':
	main()
