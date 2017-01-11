import time 
# Credit goes to:
# https://www.binarytides.com/receive-full-data-with-the-recv-socket-function-in-python/
def recv_timeout(the_socket,timeout=2):
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
            data = the_socket.recv(8192).decode()
            if data:
                total_data.append(data)
                begin = time.time()
            else:
                time.sleep(0.1)
        except:
            pass 
    return ''.join(total_data)