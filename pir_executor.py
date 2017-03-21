from random import random, uniform
import array
class PIRExecutor():
	def __init__(self):
		pass

	def _getRandomBernouille(self, random_gen):
		r = random()
		if r < random_gen:
			return 1
		return 0

	def _genRandomVector(self, size, sumEven, random_gen = 0.4):
		vector_sum = 0
		v = []
		while vector_sum == 0:
			vector_sum = 0
			set_indexes = []
			v = []
			for i in range(size):
				value = self._getRandomBernouille(random_gen)
				if value == 1:
					set_indexes.append(i)
				v.append(value)
			vector_sum = sum(v)

		if sumEven:
			if vector_sum % 2 == 0:
				return v
			if vector_sum % 2 != 0:
				index = int(uniform(0, len(set_indexes)))
				v[set_indexes[index]] = 0
				return v
		elif not sumEven:
			if vector_sum % 2 != 0:
				return v
			if vector_sum % 2 == 0:
				index = int(uniform(0, len(set_indexes)))
				v[set_indexes[index]] = 0
				return v

	def stringXorer(self, a, b):
		if type(a) is str:
			a = a.encode('utf-8')
		if type(b) is str:
			b = b.encode('utf-8')

		array_a = array.array('B', a)
		array_b = array.array('B', b)
		while(len(array_a) < len(array_b)):
			array_a.append(0)
		while(len(array_b) < len(array_a)):
			array_b.append(0)
		xored_array = array.array('B',[])
		for i in range(len(array_a)):
			xored_array.append(array_a[i] ^ array_b[i])
		stringify = xored_array.tostring()
		return stringify

	def _getMessagePack(self, index, size, dbnum):
		m = []
		for i in range(size):
			if i == index:
				v = self._genRandomVector(dbnum, False)
			else:
				v = self._genRandomVector(dbnum, True)
			m.append(v)
		return m

	def getMessagePack(self, index, size, dbnum):
		## return a transposed list of messages, ready to be sent
		return [list(i) for i in zip(*self._getMessagePack(index,size, dbnum))]


if __name__ == '__main__':
	index = 1
	size = 1000
	pir_executor = PIRExecutor()
	m = pir_executor.getMessagePack(index, size)
