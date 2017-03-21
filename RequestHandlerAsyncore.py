import asyncore
from PirSocket import PIRSocket
from epspvt_utils import ProtocolNumber


class RequestHandler(asyncore.dispatcher_with_send):
    def setData(self, callback_data=None):
        if callback_data:
            self.callback_data = callback_data

    def handle_read(self):
        self.socket = PIRSocket(self.socket)
        local_total = []
        data = self.recv(8192)
        if data:
            number, msg = (data[:ProtocolNumber.PROTOCOL_BYTE_NUMBER],
                           data[ProtocolNumber.PROTOCOL_BYTE_NUMBER:])
            number = int.from_bytes(number, byteorder='big')
            number -= len(msg)
            local_total.append(msg)
            while number > 0:
                data = self.recv(8192)
                if data:
                    local_total.append(data)
                    number -= len(data)
            data = b''.join(local_total)
            return data
        return None
