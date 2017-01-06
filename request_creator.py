from binascii import hexlify, unhexlify
from enum import Enum
import json

class RequestType(Enum):
	    publish_data = 1
	    request_data = 2

class RequestCreator():

	def __init__(self):
		pass

	def get_all_mixnode_request(self, source):
		request = {
			'type': RequestType.request_data.value,
			'payload': []
		}
		data_string = json.dumps(request)
		serialized_destination = {
			'ip':source['ip'],
			'port': int(source['port'])
		}
		return (data_string, serialized_destination)

	def post_key_request(self, destination, data):
		### This is how to retreive back the EC2Point export
		# debug_data = hexlify(public_key[2].export()).decode('utf-8')
		# print (public_key[2].export())
		# print (unhexlify(debug_data.encode()))
		###

		public_key_in_utf8 = {
			'type': RequestType.publish_data.value,
			'payload': {
				'id': hexlify(data['id']).decode('utf-8'),
				'pk': hexlify(data['pk'].export()).decode('utf-8')
			}
		}
		data_string = json.dumps(public_key_in_utf8)
		serialized_destination = {
			'ip':destination['ip'], 
			'port':int(destination['port'])
		}
		return (data_string, serialized_destination)