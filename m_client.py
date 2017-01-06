from request_creator import RequestCreator
from network_sender import NetworkSender
import argparse

class Client:
	def __init__(self, public_key_server):
		self.network_sender = NetworkSender()
		self.public_key_server = public_key_server
	
	def getList(self, source):
		request_creator = RequestCreator()
		data_string, serialized_destination = request_creator.get_all_mixnode_request(source)
		response = self.network_sender.send_data(data_string, serialized_destination)
		print (data_string, serialized_destination)
		return response

	def fetch_data(self, index):
		mixnode_list = self.getList({
				'ip': self.public_key_server['ip'],
				'port': self.public_key_server['port']
			})
		print (mixnode_list)

def parse():
	parser = argparse.ArgumentParser()
	parser.add_argument('-f', '--file', help = "The IP address will be stored in this file. Alternatively a default file will be provided.")
	parser.add_argument('pkserver', help = "Specify the public IP address of the server where public keys will be stored.")
	parser.add_argument('port', help="Specify the port where the server is listening for connections")
	args = parser.parse_args()
	print (args)
	return args

def main():
	args = vars(parse())
	client = Client({
		'ip':args['pkserver'],
		'port': args['port']
		})
	client.fetch_data(1)

if __name__ == '__main__':
	main()