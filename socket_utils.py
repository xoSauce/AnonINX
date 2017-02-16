import time 
from petlib.pack import decode
# Credit goes to:
# https://www.binarytides.com/receive-full-data-with-the-recv-socket-function-in-python/

def recv_timeout_petlib_pack(the_socket, timeout=0.5):
    the_socket.setblocking(0)  
    total_data=[];
    data=''; 
    begin=time.time()
    while 1:
        if total_data and time.time()-begin > timeout:
            break
        elif time.time()-begin > timeout*2:
            break
        try:
            data = the_socket.recv(1024)
            if data:
                total_data.append(data)
                begin = time.time()
            else:
                time.sleep(0.1)
        except:
            pass 
    string = b''.join(total_data)
    if string == b'':
        return ''
    return decode(string)

def recv_timeout(the_socket,timeout=0.5):
    the_socket.setblocking(0)  
    total_data=[];
    data=''; 
    begin=time.time()
    while 1:
        if total_data and time.time()-begin > timeout:
            break
        elif time.time()-begin > timeout*2:
            break
        try:
            data = the_socket.recv(1024).decode()
            if data:
                total_data.append(data)
                begin = time.time()
            else:
                time.sleep(0.1)
        except:
            pass 
    return ''.join(total_data)