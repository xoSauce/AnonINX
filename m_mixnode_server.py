from mix import MixNode
from epspvt_utils import Debug
from mixnode_listener import MixNodeListener
from mixnode_sender import MixNodeSender
from logger import *
from request_creator import PortEnum, PortEnumDebug
import argparse
import asyncore
from threading import Thread, Lock

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

	mixNode = MixNode(broker_config, pool_size = 3)
	response = mixNode.publish_key()
	mixport = int(portEnum.mix.value)
	backlog_lock = Lock()
	mixNodeListener = MixNodeListener('0.0.0.0', portEnum.mix.value, mixNode, backlog_lock)
	loop_thread = Thread(target=asyncore.loop, name="mixnode listneer")
	loop_thread.start()
	cache_sender = Thread(target=mixNode.handleCache, args=(backlog_lock,), name ="cache handler")
	cache_sender.start()
	mixNodeSender = MixNodeSender(mixNode.mix_pool)
	mixNodeSender.start()

if __name__ == '__main__':
	main()
