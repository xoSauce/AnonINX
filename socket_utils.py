import time
from petlib.pack import decode
from epspvt_utils import ProtocolNumber
# Credit goes to:
# https://www.binarytides.com/receive-full-data-with-the-recv-socket-function-in-python/

def recv_timeout_petlib_pack(the_socket, timeout=0.15):
    the_socket.setblocking(0)
    total_data=[];
    data='';
    begin=time.time()
    isEmpty =0
    while 1:
        if total_data and time.time()-begin > timeout:
            break
        elif isEmpty > 20:
            break
        try:
            data = the_socket.recv(4096)
            if data:
                total_data.append(data)
                begin = time.time()
            else:
                isEmpty += 1
                time.sleep(0.05)
        except:
            pass
    string = b''.join(total_data)
    if string == b'':
        return ''
    return decode(string)

def recv_timeout(the_socket, timeout=None):
    local_total = []
    if timeout:
        the_socket.settimeout(timeout)
    data = the_socket.recv(8192)
    if data:
        number, msg = (data[:ProtocolNumber.PROTOCOL_BYTE_NUMBER],
                       data[ProtocolNumber.PROTOCOL_BYTE_NUMBER:])
        number = int.from_bytes(number, byteorder='big')
        number -= len(msg)
        local_total.append(msg)
        while number > 0:
            data = the_socket.recv(8192)
            if data:
                local_total.append(data)
                number -= len(data)
        data = b''.join(local_total)
        return data
