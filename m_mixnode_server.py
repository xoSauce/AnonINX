from mix import MixNode
from mixnode_listener import MixNodeListener
import argparse

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
	mixNode = MixNode(server_config)
	response = mixNode.publish_key()
	print (response)
	mixNodeListener = MixNodeListener(8081, mixNode)
	mixNodeListener.listen()

if __name__ == '__main__':
	main()
