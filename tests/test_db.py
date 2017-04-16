import sys, os
myPath = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, myPath + '/../')

from db import DbNode
from unittest.mock import MagicMock
from pir_executor import PIRExecutor
def test_db():
    dbNode = DbNode({'database': 'tests/db_json'})
    requested_index = 2
    assert(requested_index <= 10) ## db_json only has 11 records
    msg = {'pir_xor': False, 'index': requested_index}
    answer = dbNode.fetch_answer(msg)
    assert(answer == 'https://facebook.com\n')
    vec = [1, 0, 1, 0, 1, 0, 0, 0, 0 ,0 ,1]
    assert(len(vec) == 11)
    executor = PIRExecutor()
    array = ["https://google.com\n\n\n", "https://facebook.com\n", "https://alibaba.com\n\n", "https://improbable.i\n"]
    expected_result = array[0]
    for i in array[1:]:
        print(expected_result)
        expected_result = executor.stringXorer(expected_result, i)
    print(expected_result)
    msg = {'pir_xor': True, 'index': vec}
    answer = dbNode.fetch_answer(msg)
    print(answer)
    assert(answer == expected_result)
