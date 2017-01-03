import sphinxmix
from sphinxmix.SphinxParams import SphinxParams

# The minimal PKI involves names of nodes and keys
from sphinxmix.SphinxNode import Nenc
from sphinxmix.SphinxClient import pki_entry
from epspvt_utils import getIp, RequestType
import mix
from binascii import hexlify, unhexlify
import sys
import argparse
import os

### Generates private and public keys
### Returns a tuple of public, private_key


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
	mix = mix.MixNode(server_config)
	public_key, private_key = keyGen(params)
	json_data, destination = prepare_sending_pk(public_key, vars(server_config))
	response = send_pk(json_data, destination)
	print (response)

if __name__ == '__main__':
	main()
