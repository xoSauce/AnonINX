import time
from petlib.pack import decode
# Credit goes to:
# https://www.binarytides.com/receive-full-data-with-the-recv-socket-function-in-python/

def recv_timeout_petlib_pack(the_socket, timeout=0.1):
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
                time.sleep(0.01)
            if data == '':
                print("IS EMPTY !!!")
        except:
            pass
    string = b''.join(total_data)
    if string == b'':
        return ''
    return decode(string)

def recv_timeout(the_socket,timeout=0.1):
    the_socket.setblocking(0)
    total_data=[];
    isEmpty = 0
    data=None;
    begin=time.time()
    while 1:
        if total_data and time.time()-begin > timeout:
            break
        elif isEmpty > 20:
            break
        try:
            data = the_socket.recv(4096).decode()
            if data:
                total_data.append(data)
                begin = time.time()
            else:
                time.sleep(0.01)
                isEmpty += 1
            if data == '':
                print("IS EMPTY !!!")
        except:
            pass
    return ''.join(total_data)
