import sys, os
myPath = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, myPath + '/../')

from mix import MixNode
from unittest.mock import MagicMock, patch, ANY
from network_sender import NetworkSender
import threading
import time
def test_mixnode():
    with patch.object(NetworkSender, 'send_data') as mock:
        mix = MixNode(None)
        lock = threading.Lock()
        t = threading.Thread(target=mix.handlePool, args=(lock,), name='test_mix')
        t.daemon = True
        t.start()
        mix.pool_item((1,0))
        mix.pool_item((2,0))
        mix.pool_item((3,0))
        mix.pool_item((4,1))
        mix.pool_item((4,1))
        time.sleep(1)
        mock.assert_called_with(ANY,ANY)

    mixnode = MixNode(None)
    socket = MagicMock()
    socket.sendall.__return_value = 'DONE'
    pair = (0,socket)
    mixnode.client_backlog.add(pair)
    mixnode.client_cache = {0:"blah"}
    t2 = threading.Thread(target=mixnode.handleCache, args=(lock,), name='test_cache')
    t2.daemon = True
    t2.start()
    time.sleep(1)
    assert(len(mixnode.client_cache) == 0)
