import socket
class PIRSocket(object):
    def __init__(self, sock = None):
        if sock:
            self._sock = sock
        else:
            self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._sock.settimeout(10*60)
        self._protocolByteNumber = 15

    def __getattr__(self, name):
        return getattr(self._sock, name)

    def getProtocolByteNumber(self):
        return self._protocolByteNumber

    def _construct_message(self, msg):
        return (len(msg)).to_bytes(self._protocolByteNumber, byteorder='big') + msg

    def send(self, msg):
        return self.sendall(msg)

    def sendall(self, msg):
        msg = self._construct_message(msg)
        try:
            self._sock.sendall(msg)
        except OSError:
            print('Client has left')

    def connect(self, *p):
        self._sock.connect(*p)
