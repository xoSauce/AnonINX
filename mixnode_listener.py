import json
import socketserver
from request_creator import RequestType
from mix import MixNode
from threading import Thread
from petlib.ec import EcPt
from binascii import unhexlify
from epspvt_utils import getGlobalSphinxParams
from logger import *
from socket_utils import recv_timeout
from request_creator import RequestCreator
from network_sender import NetworkSender
from sphinxmix.SphinxClient import Relay_flag, Dest_flag, Surb_flag
from broker_communicator import BrokerCommunicator
from epspvt_utils import Debug
from petlib.pack import encode, decode
import logger
import time
from datetime import datetime


class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    pass


class service(socketserver.BaseRequestHandler):
    def handle(self):
        try:
            self.mixnode = self.server.mixnode
            self.network_sender = NetworkSender()
            self.mix_port = self.server.mixport
            raw_data = recv_timeout(self.request)
            data = json.loads(raw_data)
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
                        {'ip': addr, 'port': self.mix_port},
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
                if client_id in self.mixnode.client_cache:
                    start = time.time()
                    operation = ''
                    response = self.mixnode.client_cache.get(client_id)
                    response = encode({"id": client_id, "response": response})
                    self.request.sendall(response)
                    self.mixnode.client_cache.pop(client_id)
                    operation = '[CLIENT_POLL] send'
                    end = time.time()
                    timestamp = datetime.fromtimestamp(
                        end - start).strftime('%M:%S')
                    logger.log_info(
                        '[TIME] MIX LISTENER {} TOOK {}'.format(operation, timestamp))
        finally:
            self.request.close()


class MixNodeListener(Thread):
    def __init__(self, port, mixnode, mixport):
        Thread.__init__(self)
        self.port = port
        self.mixnode = mixnode
        self.mixport = mixport

    def listen(self):
        ThreadedTCPServer.allow_reuse_address = True
        server = ThreadedTCPServer(('', self.port), service)
        server.mixnode = self.mixnode
        server.mixport = self.mixport
        try:
            server.serve_forever()
        finally:
            print("server closing")
            server.server_shutdown()

    def run(self):
        self.listen()
