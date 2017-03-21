# import json
# import socketserver
# from request_creator import RequestType
# from threading import Thread
# from petlib.ec import EcPt
# from binascii import unhexlify
# from epspvt_utils import getGlobalSphinxParams
# from logger import *
# from socket_utils import recv_timeout
# from request_creator import RequestCreator
# from network_sender import NetworkSender
# from sphinxmix.SphinxClient import Relay_flag, Dest_flag, Surb_flag
# from broker_communicator import BrokerCommunicator
# from epspvt_utils import Debug
# import logger
# import time
# from datetime import datetime
import socket
import asyncore
import time
import logger
import json
from mix import MixNode
from petlib.pack import decode
from datetime import datetime
from request_creator import RequestCreator, RequestType
from sphinxmix.SphinxClient import Relay_flag, Dest_flag, Surb_flag
from RequestHandlerAsyncore import RequestHandler
from binascii import unhexlify
from network_sender import NetworkSender
#
#
# class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
#     pass
#
#
# class service(socketserver.BaseRequestHandler):
#     def handle(self):
#         try:
#             self.mixnode = self.server.mixnode
#             self.network_sender = NetworkSender()
#             self.mix_port = self.server.mixport
#             raw_data = recv_timeout(self.request)
#             data = json.loads(raw_data)
#             if data['type'] == RequestType.push_to_mix.value:
#                 start = time.time()
#                 operation = ''
#                 data = decode(unhexlify(data['payload']))
#                 header = data['header']
#                 delta = data['delta']
#                 result = self.mixnode.process(header, delta)
#                 if result[0] == Relay_flag:
#                     flag, addr, header, delta = result
#                     json_data, dest = RequestCreator().post_msg_to_mix(
#                         {'ip': addr, 'port': self.mix_port},
#                         {'header': header, 'delta': delta}
#                     )
#                     self.mixnode.pool_item((json_data, dest))
#                     operation = '[RELAY_FLAG] pool'
#                 elif result[0] == Dest_flag:
#                     flag, msg, dest, _ = result
#                     json_data, dest = RequestCreator().post_msg_to_db(dest, msg)
#                     self.network_sender.send_data(json_data, dest)
#                     operation = '[DEST_FLAG] send'
#                 elif result[0] == Surb_flag:
#                     flag, dest, myid, delta = result
#                     msg = {'myid': myid, 'delta': delta}
#                     self.mixnode.client_cache.setdefault(myid, []).append(msg)
#                     operation = '[SURB_FLAG] cache'
#                 end = time.time()
#                 timestamp = datetime.fromtimestamp(
#                     end - start).strftime('%M:%S')
#                 logger.log_info(
#                     '[TIME] MIX LISTENER {} TOOK {}'.format(operation, timestamp))
#             elif data['type'] == RequestType.client_poll.value:
#                 client_id = unhexlify(data['id'])
#                 if client_id in self.mixnode.client_cache:
#                     start = time.time()
#                     operation = ''
#                     response = self.mixnode.client_cache.get(client_id)
#                     response = encode({"id": client_id, "response": response})
#                     self.request.sendall(response)
#                     self.mixnode.client_cache.pop(client_id)
#                     operation = '[CLIENT_POLL] send'
#                     end = time.time()
#                     timestamp = datetime.fromtimestamp(
#                         end - start).strftime('%M:%S:%f')
#                     logger.log_info(
#                         '[TIME] MIX LISTENER {} TOOK {}'.format(operation, timestamp))
#         finally:
#             self.request.close()
#
#
# class MixNodeListener(Thread):
#     def __init__(self, port, mixnode, mixport):
#         Thread.__init__(self)
#         self.port = port
#         self.mixnode = mixnode
#         self.mixport = mixport
#
#     def listen(self):
#         ThreadedTCPServer.allow_reuse_address = True
#         server = ThreadedTCPServer(('', self.port), service)
#         server.mixnode = self.mixnode
#         server.mixport = self.mixport
#         try:
#             server.serve_forever()
#         finally:
#             print("server closing")
#             server.server_shutdown()
#
#     def run(self):
#         self.listen()

class MixListenerHandler(RequestHandler):
    def setData(self, mixnode, backlog_lock, mixport, callback_data=None):
        super().setData(callback_data)
        self.mixnode = mixnode
        self.network_sender = NetworkSender()
        self.backlog_lock = backlog_lock
        self.mixport = mixport

    def handle_read(self):
        data = super().handle_read()
        if data:
            data = json.loads(data.decode())
            if data['type'] == RequestType.push_to_mix.value:
                start = time.time()
                operation = ''
                data = decode(unhexlify(data['payload']))
                header = data['header']
                delta = data['delta']
                result = self.mixnode.process(header, delta)
                if result[0] == Relay_flag:
                    flag, addr, header, delta = result
                    json_data, dest = RequestCreator().post_msg_to_mix(
                        {'ip': addr, 'port': self.mixport},
                        {'header': header, 'delta': delta}
                    )
                    self.mixnode.pool_item((json_data, dest))
                    operation = '[RELAY_FLAG] pool'
                elif result[0] == Dest_flag:
                    flag, msg, dest, _ = result
                    json_data, dest = RequestCreator().post_msg_to_db(dest, msg)
                    self.network_sender.send_data(json_data, dest)
                    operation = '[DEST_FLAG] send'
                elif result[0] == Surb_flag:
                    flag, dest, myid, delta = result
                    msg = {'myid': myid, 'delta': delta}
                    self.mixnode.client_cache.setdefault(myid, []).append(msg)
                    operation = '[SURB_FLAG] cache'
                end = time.time()
                timestamp = datetime.fromtimestamp(
                    end - start).strftime('%M:%S')
                logger.log_info(
                    '[TIME] MIX LISTENER {} TOOK {}'.format(operation, timestamp))
            elif data['type'] == RequestType.client_poll.value:
                client_id = unhexlify(data['id'])
                with self.backlog_lock:
                    self.mixnode.client_backlog.add((client_id, self.socket))


class MixNodeListener(asyncore.dispatcher):
    def __init__(self, host, port, mixnode, backlog_lock, mixport):
        asyncore.dispatcher.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.set_reuse_addr()
        self.bind((host, port))
        self.listen(5)
        self.mixnode = mixnode
        self.backlog_lock = backlog_lock
        self.mixport = mixport

    def handle_accept(self):
        pair = self.accept()
        if pair is not None:
            sock, addr = pair
            handler = MixListenerHandler(sock)
            handler.setData(self.mixnode, self.backlog_lock, self.mixport)
