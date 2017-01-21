from request_creator import RequestCreator
from network_sender import NetworkSender
import json

class BrokerCommunicator:
	def __init__(self):
		self.network_sender = NetworkSender()

	def getMixNodeList(self, source):
		request_creator = RequestCreator()
		data_string, serialized_destination = request_creator.get_all_mixnode_request(source)
		response = self.network_sender.send_data_wait(data_string, serialized_destination)
		return json.loads(response)

	def getDBList(self, source):
		request_creator = RequestCreator()
		data_string, serialized_destination = request_creator.get_all_db_request(source)
		response = self.network_sender.send_data_wait(data_string, serialized_destination)
		return json.loads(response)
