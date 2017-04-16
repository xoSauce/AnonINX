import sys, os
myPath = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, myPath + '/../')

from message_creator import MessageCreator
from m_client import Client
from request_creator import PortEnumDebug
from epspvt_utils import SecurityParameters, getGlobalSphinxParams
from unittest.mock import MagicMock
from petlib.ec import EcPt
def test_generateMessages():
    portEnum = PortEnumDebug
    thing = Client({
        'ip': '0.0.0.0',
        'port': portEnum.broker.value
    })
    group = getGlobalSphinxParams().group.G
    dummy_key = group.generator().export()
    SecurityParameters.NUMBER_OF_REQUESTS = 12
    thing.db_list = [(0, dummy_key),(1, dummy_key), (2, dummy_key)]
    thing.mixnode_list = {'a': dummy_key, 'b': dummy_key, 'c': dummy_key}
    msgCreator = MessageCreator(thing)
    requested_index = 5
    record_size = 100
    requested_db = 2
    for i in range(0, 20):
        random_indexes = msgCreator._generate_random_indexes(5, record_size)
        print(random_indexes)
        assert(len(random_indexes) == SecurityParameters.NUMBER_OF_REQUESTS - 1)
        assert(requested_index not in random_indexes)

    messages = msgCreator.generate_messages(requested_index, requested_db, record_size,
        portEnum, pir_xor = False)
    len_0 = len(messages[0])
    for key, value in messages.items():
        assert(len(value) == len_0)

    messages = msgCreator.generate_messages(requested_index, requested_db, record_size,
        portEnum, pir_xor = True)
    assert(len(messages) == len(thing.db_list))
    first_message = messages[0]
    for key,value in messages.items():
        assert(len(value) == len(first_message))
