from db import DbNode
from epspvt_utils import Debug
from db_listener import DBListener
from logger import *
from request_creator import PortEnum, PortEnumDebug
from threading import Thread
import asyncore
import argparse

def parse():
	parser = argparse.ArgumentParser()
	parser.add_argument('-db', '--database', help = "specify the db to cache")
	parser.add_argument('-d', '--debug', action='store_true', help = "Debug mode will route all the public ips to 0.0.0.0")
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

	dbNode = DbNode(broker_config)
	response = dbNode.publish_key()
	dbListener = DBListener('localhost', portEnum.db.value, portEnum.mix.value, dbNode)
	loop_thread = Thread(target=asyncore.loop, name="db loop")
	loop_thread.start()

if __name__ == '__main__':
	main()
