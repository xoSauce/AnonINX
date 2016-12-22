import socket
import json
from threading import Thread
from server_key_publisher import Broker
from epspvt_utils import RequestType
class Client(Thread):

    def __init__(self, socket, address, broker):
        Thread.__init__(self)
        self.sock = socket
        self.addr = address
        self.broker = broker
        self.start()

    def run(self):
        data = json.loads(self.sock.recv(1024).decode())
        if data['type'] == RequestType.publish_data.value:
            self.broker.register(data['payload'])
            self.sock.send(b'Key will be published.')
            print(self.broker.get_cache())
        elif data['type'] == RequestType.request_data.value:
            pk = self.broker.get_cache_entry(data['payload'])
            self.broker.send(pk.encode())

def main():
    try:
        serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        serversocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        host = "0.0.0.0" # any host
        port = 8080
        serversocket.bind((host, port))
        serversocket.listen(5)
        print ('server listening on {}'.format(port))
        broker = Broker()
        while 1:
            clientsocket, address = serversocket.accept()
            Client(clientsocket, address, broker)
    finally:
        serversocket.close()

if __name__ == '__main__':
    main()