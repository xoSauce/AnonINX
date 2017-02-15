from mix import MixNode
from epspvt_utils import Debug
from mixnode_listener import MixNodeListener
from logger import *
from requestCreator import PortEnum, PortEnumDebug
import argparse

def parse():
	parser = argparse.ArgumentParser()
	parser.add_argument('-f', '--file', help = "The IP address will be stored in this file. Alternatively a default file will be provided.")
	parser.add_argument('-d', '--debug', action='store_true', help = "The IP address will be stored in this file. Alternatively a default file will be provided.")
	parser.add_argument('pkserver', help = "Specify the public IP address of the server where public keys will be stored.")
	parser.add_argument('port', help="Specify the port where the server is listening for connections")
	args = parser.parse_args()
	return args

def main():
	log_init("m_mixnode_server.log")
	broker_config = vars(parse())
	
	portEnum = PortEnum
	if broker_config['debug']:
		Debug.dbg = True
		portEnum = PortEnumDebug


	mixNode = MixNode(broker_config)
	response = mixNode.publish_key()
	mixNodeListener = MixNodeListener(portEnum.mix.value, mixNode)
	mixNodeListener.listen()

if __name__ == '__main__':
	main()
