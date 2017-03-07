import socket
from threading import Thread
from logger import *
class GenericListener(Thread):
    def __init__(self, port, host = "0.0.0.0"):
        Thread.__init__(self)
        self.host = host
        self.port = port
        self.serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.serversocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.serversocket.bind((self.host, self.port))
        self.serversocket.listen(5)

    def run(self):
        log_debug('server listening on {}'.format(self.port))
        pass

if __name__ == '__main__':
    main()
