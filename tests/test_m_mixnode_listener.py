import sys, os
myPath = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, myPath + '/../')

from mixnode_listener import MixNodeListener
from m_client import Client
from message_creator import MessageCreator
from request_creator import PortEnumDebug
from epspvt_utils import SecurityParameters, getGlobalSphinxParams
from mix import MixNode
from PirSocket import PIRSocket
from network_sender import NetworkSender
import asyncore
from unittest.mock import MagicMock
from sphinxmix.SphinxClient import Relay_flag, Dest_flag, Surb_flag
from threading import Lock
def test_listener():
    portEnum = PortEnumDebug
    thing = Client({
        'ip': '0.0.0.0',
        'port': portEnum.broker.value
    })
    group = getGlobalSphinxParams().group.G
    dummy_key = group.generator().export()
    SecurityParameters.NUMBER_OF_REQUESTS = 3
    thing.db_list = [(0, dummy_key),(1, dummy_key), (2, dummy_key)]
    thing.mixnode_list = {'0.0.0.0': dummy_key, '0.0.0.0': dummy_key, '0.0.0.0': dummy_key}
    msgCreator = MessageCreator(thing)
    requested_index = 5
    record_size = 100
    requested_db = 2
    messages = msgCreator.generate_messages(requested_index, requested_db, record_size,
        portEnum, pir_xor = False)
    host = '0.0.0.0'
    port = portEnum.mix.value
    mix = MixNode(None)
    mix.process = MagicMock(return_value=(Relay_flag, None, None, None))
    listener = MixNodeListener(host, port, mix, (Lock(), Lock()), port)#
    network_sender = NetworkSender()
    json, dest = messages[0][0]
    network_sender.send_data(json, dest)
    asyncore.loop(count=2)
    assert(len(mix.mix_pool.getContents()) == 1)
