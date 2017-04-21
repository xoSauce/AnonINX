import sys, os
myPath = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, myPath + '/../')

from pir_executor import PIRExecutor
from binary_encoderdecoder import BinaryEncoderDecoder
def test_PIR_getMessagePack():
	index = 1
	size = 100
	for i in range(20):
		pir_executor = PIRExecutor()
		m = pir_executor._getMessagePack(index, size, 5)
		l = m[index]
		## assert requested is odd
		assert sum(l) % 2 != 0
		## assert all the rest are even
		for j in range(len(m)):
			if j == index:
				continue
			assert sum(m[j]) % 2 == 0

def test_PIR_xorer():
	for i in range(100):
		pir_executor = PIRExecutor()
		a = 'HelloWorld'
		b = 'GoodbyeCruelWorld'
		result = pir_executor.stringXorer(a,b)
		result2 = pir_executor.stringXorer(result, b).split(b'\0', 1)[0]
		assert result2.decode() == a
		result3 = pir_executor.stringXorer(result, a).split(b'\0', 1)[0]
		assert result3.decode() == b

def test_PIR_xorer_list():
	messages = {
		0: 'FakeBlahBlah',
		1: 'Real',
		2: 'FakeBlahBlah',
		3: 'FakeBlahBlah',
		4: 'FakeBlahBlah',
		5: 'Real',
		6: 'Real'
	}

	for i in range(0,100):
		pir_executor = PIRExecutor()
		message = messages[0]
		for m in range(1, len(messages)):
			message = pir_executor.stringXorer(message, messages[m])
	message = message.split(b'\0', 1)[0]
	assert message.decode() == 'Real'

	messages = {
		0: 'FakeBlahBlah',
		1: 'Real',
		2: 'FakeBlahBlah',
		3: 'FakeBlahBlah',
		4: 'FakeBlahBlah',
		5: 'Real',
	}
	for i in range(0,100):
		pir_executor = PIRExecutor()
		message = messages[0]
		for m in range(1, len(messages)):
			message = pir_executor.stringXorer(message, messages[m])

	message = message.split(b'\0', 1)[0]
	assert message.decode() == ''

def test_PIR_protocol():
	messages = {
		0: 'Fake0',
		1: 'Real1',
		2: 'Fake2',
		3: 'Fake3',
		4: 'Fake4',
		5: 'Fake5'
	}
	messages = {
		0: "Annaaa",
		1: "George",
		2: "Danaaa",
		3: "Johnaa",
		4: "Doeaaa",
		5: "Earlaa",
		6: "Jensaa",
		7: "Glensa",
	}
	decoder = BinaryEncoderDecoder()
	for index in range(0, len(messages)):
		print("INDEX", index)
		size = len(messages)
		print(size)
		pir_executor = PIRExecutor()
		m = pir_executor.getMessagePack(index, size, 5)
		db_returns = []
		for row in m:
			row = decoder.decode_binary(row, len(messages))
			print("ROW", row)
			message = ''
			for i in range(0, len(row)):
				if row[i] == 1:
					if message == '':
						message = messages[i]
					else:
						message = pir_executor.stringXorer(message, messages[i])
			db_returns.append(message)
		actual_message = db_returns[0]
		for i in range(1, len(db_returns)):
			actual_message = pir_executor.stringXorer(actual_message, db_returns[i])
		actual_message = actual_message.split(b'\0', 1)[0]
		assert(actual_message.decode() == messages[index])
