# import socket
# import json
# from generic_listener import GenericListener
# from request_creator import RequestType, RequestCreator
# from mix import MixNode
# from threading import Thread
# from petlib.ec import EcPt
# from binascii import unhexlify
# from epspvt_utils import getGlobalSphinxParams
# from socket_utils import recv_timeout
# from network_sender import NetworkSender
# from sphinxmix.SphinxClient import Relay_flag
# from broker_communicator import BrokerCommunicator
# from petlib.pack import encode, decode
# from sphinxmix.SphinxClient import create_surb, package_surb, rand_subset
#
# class Worker(Thread):
#       def __init__(self, socket, dbnode, db_port, mixport):
#               Thread.__init__(self)
#               self.sock = socket
#               self.dbnode = dbnode
#               self.db_port = db_port
#               self.mixport = mixport
#               self.network_sender = NetworkSender()
#               self.start()
#
#       def run(self):
#               raw_data = recv_timeout(self.sock)
#               data = json.loads(raw_data)
#               print("LOADED", data, type(data))
#               iv = unhexlify(data["iv"].encode())
#               text = unhexlify(data["text"].encode())
#               pk = EcPt.from_binary(unhexlify(data["pk"].encode()), getGlobalSphinxParams().group.G)
#               tag = unhexlify(data["tag"].encode())
#               decrypted_msg = decode(self.dbnode.decrypt(iv, text, pk, tag))
#               request_type = decrypted_msg['request_type']
#               client_pk = decrypted_msg['pk'][2]
#               print("request_type", request_type)
#               if request_type == RequestType.get_db_size.value:
#                       record_size = self.dbnode.getRecordsSize()
#                       reply = encode(record_size)
#                       self.sock.send(reply)
#               elif request_type == RequestType.push_to_db.value:
#                       answer = self.dbnode.fetch_answer(decrypted_msg)
#                       reply = encode(answer)
#                       print(reply)
#                       encrypted_reply = encode(self.dbnode.encrypt(reply, client_pk))
#                       nymtuple = decrypted_msg['nymtuple']
#                       first_node = decode(nymtuple[0])
#                       header, delta = package_surb(getGlobalSphinxParams(), nymtuple, encrypted_reply)
#                       mix_list = self.dbnode.get_mixnode_list()
#                       json_data, dest = RequestCreator().post_msg_to_mix(
#                               {'ip': first_node[1], 'port': self.mixport},
#                               {'header': header, 'delta': delta}
#                       )
#                       self.network_sender.send_data(json_data, dest)
#
# class DBListener(GenericListener):
#       def __init__(self, db_port, mixport, dbnode):
#               super().__init__(db_port)
#               self.dbnode = dbnode
#               self.mixport = mixport
#
#       def run(self):
#               super().run()
#               try:
#                       while 1:
#                               clientsocket, address = self.serversocket.accept()
#                               Worker(clientsocket, self.dbnode, self.port, self.mixport)
#               finally:
#                       self.serversocket.close()

from RequestHandlerAsyncore import RequestHandler
from petlib.ec import EcPt
from binascii import unhexlify
from epspvt_utils import getGlobalSphinxParams
from network_sender import NetworkSender
from petlib.pack import encode, decode
from request_creator import RequestType, RequestCreator
from sphinxmix.SphinxClient import create_surb
from sphinxmix.SphinxClient import package_surb
from sphinxmix.SphinxClient import rand_subset
import socket
import asyncore
import json
import time
from logger import log_info

class DbListenerHandler(RequestHandler):
    def setData(self, dbnode, mixport, callback_data=None):
        super().setData(callback_data)
        self.dbnode = dbnode
        self.mixport = mixport
        self.network_sender = NetworkSender()

    def handle_read(self):
        data = super().handle_read()
        if data:
            data = json.loads(data.decode())
            iv = unhexlify(data["iv"].encode())
            text = unhexlify(data["text"].encode())
            pk = EcPt.from_binary(
                    unhexlify(data["pk"].encode()), getGlobalSphinxParams().group.G)
            tag = unhexlify(data["tag"].encode())
            decrypted_msg = decode(self.dbnode.decrypt(iv, text, pk, tag))
            request_type = decrypted_msg['request_type']
            client_pk = decrypted_msg['pk'][2]
            if request_type == RequestType.get_db_size.value:
                record_size = self.dbnode.getRecordsSize()
                reply = encode(record_size)
                self.socket.sendall(reply)
            elif request_type == RequestType.push_to_db.value:
                t1 = time.perf_counter()
                print("TRYING TO FETCH")
                answer = self.dbnode.fetch_answer(decrypted_msg)
                print("ANSWER:", answer)
                reply = encode(answer)
                encrypted_reply = encode(self.dbnode.encrypt(reply, client_pk))
                nymtuple = decrypted_msg['nymtuple']
                first_node = decode(nymtuple[0])
                header, delta = package_surb(
                        getGlobalSphinxParams(), nymtuple, encrypted_reply)
                self.dbnode.get_mixnode_list()
                json_data, dest = RequestCreator().post_msg_to_mix(
                        {'ip': first_node[1], 'port': self.mixport},
                        {'header': header, 'delta': delta}
                )
                t2 = time.perf_counter()
                elapsed_time = (t2-t1)
                log_info("TIME ELAPSED: {}".format(elapsed_time))
                self.network_sender.send_data(json_data, dest)


class DBListener(asyncore.dispatcher):
    def __init__(self, host, port, mixport, dbNode):
        asyncore.dispatcher.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.set_reuse_addr()
        self.bind((host, port))
        self.listen(5)
        self.dbnode = dbNode
        self.mixport = mixport

    def handle_accept(self):
        pair = self.accept()
        if pair is not None:
            sock, addr = pair
            handler = DbListenerHandler(sock)
            handler.setData(self.dbnode, self.mixport)
