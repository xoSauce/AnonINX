from db import DbNode
from epspvt_utils import Debug
from db_listener import DBListener
from logger import *
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
	
	if broker_config['debug']:
		Debug.dbg = True

	dbNode = DbNode(broker_config)
	response = dbNode.publish_key()
	dbListener = DBListener(8082, dbNode)
	dbListener.listen()

if __name__ == '__main__':
	main()
