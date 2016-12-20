import socket
import json
from threading import Thread

class Client(Thread):
    def __init__(self, socket, address):
        Thread.__init__(self)
        self.sock = socket
        self.addr = address
        self.start()

    def run(self):
            data = json.loads(self.sock.recv(1024).decode())
            self.sock.send(b'Key will be published.')


def main():
    serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    host = "0.0.0.0" # any host
    port = 8080
    print (host)
    print (port)
    serversocket.bind((host, port))
    serversocket.listen(5)
    print ('server listening on {}'.format(port))
    while 1:
        clientsocket, address = serversocket.accept()
        print (address)
        Client(clientsocket, address)


if __name__ == '__main__':
    main()