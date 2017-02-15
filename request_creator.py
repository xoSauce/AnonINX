from binascii import hexlify, unhexlify
from enum import Enum
from epspvt_utils import Debug
from petlib.pack import encode
import json

class RequestType(Enum):
	    publish_mix_data = 1
	    publish_db_data = 2
	    request_mix_list = 3
	    request_db_list = 4
	    push_to_mix = 5
	    push_to_db = 6
	    push_to_client = 7

class PortEnum(Enum):
		broker  = 8080
		mix = 8080
		db = 8080
		client = 8080

class PortEnumDebug(Enum):
		broker  = 8080
		mix = 8081
		db = 8082
		client = 8083

class RequestCreator():

	def __init__(self):
		if Debug.dbg:
			self.portEnum = PortEnumDebug
		else:
			self.portEnum = PortEnum

	def get_all_mixnode_request(self, source):
		request = {
			'type': RequestType.request_mix_list.value,
			'payload': []
		}
		data_string = json.dumps(request)
		serialized_destination = {
			'ip':source['ip'],
			'port': int(source['port'])
		}
		return (data_string, serialized_destination)

	def get_all_db_request(self, source):
		request = {
			'type': RequestType.request_db_list.value,
			'payload': []
		}
		data_string = json.dumps(request)
		serialized_destination = {
			'ip':source['ip'],
			'port': int(source['port'])
		}
		return (data_string, serialized_destination)

	def post_msg_to_mix(self, destination, data):
		request = {
			'type': RequestType.push_to_mix.value,
			'payload': {
				'header_0': hexlify(data['header'][0].export()).decode('utf-8'),
				'header_1': hexlify(data['header'][1]).decode('utf-8'),
				'header_2': hexlify(data['header'][2]).decode('utf-8'),
				'delta': hexlify(data['delta']).decode('utf-8')
			}
		}
		data_string = json.dumps(request)
		serialized_destination = {
			'ip': destination['ip'],
			'port': int(destination['port'])
		}
		return (data_string, serialized_destination)

	def post_msg_to_db(self, destination, data):
		request = {
			'type': RequestType.push_to_db.value,
			'payload': data
		}
		data_string = json.dumps(request)
		serialized_destination = {
			'ip': destination[0],
			'key': destination[1],
			'port': int(destination[2])
		}
		return (data_string, serialized_destination)

	def post_msg_to_client(self, destination, key, data):
		request = {
			'type': RequestType.push_to_client.value,
			'payload': hexlify(encode(data)).decode('utf-8')
		}
		data_string = json.dumps(request)
		serialized_destination = {
			'ip': destination,
			'port': self.portEnum.client.value
		}
		print(serialized_destination)
		return (data_string, serialized_destination)

	def post_mix_key_request(self, destination, data):
		public_key_in_utf8 = {
			'type': RequestType.publish_mix_data.value,
			'payload': {
				'id': data['id'],
				'pk': hexlify(data['pk'].export()).decode('utf-8')
			}
		}
		data_string = json.dumps(public_key_in_utf8)
		serialized_destination = {
			'ip':destination['ip'], 
			'port':int(destination['port'])
		}
		return (data_string, serialized_destination)

	def post_db_key_request(self, destination, data):
		public_key_in_utf8 = {
			'type': RequestType.publish_db_data.value,
			'payload': {
				'id': data['id'],
				'pk': hexlify(data['pk'].export()).decode('utf-8')
			}
		}
		data_string = json.dumps(public_key_in_utf8)
		serialized_destination = {
			'ip':destination['ip'], 
			'port':int(destination['port'])
		}
		return (data_string, serialized_destination)