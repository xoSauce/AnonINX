from random import SystemRandom
class MessageCreator:
	def __init__(self, client, dbnum):
		self.client = client
		self.dbnum = dbnum

	def _generate_random_indexes(self, requested_index, index_limit):
		gen = SystemRandom()
		random_set = set()
		while len(random_set) < self.dbnum * 2 - 1:
			num = gen.randrange(index_limit)
			if num == requested_index:
				continue
			random_set.add(num)
		return random_set

	def generate_messages(self, requested_index, requested_db, record_size = 100):
		indexes = self._generate_random_indexes(requested_index, record_size)
		real_message = self.client.package_message(requested_index, requested_db)
		db_index = {}
		for i in range(self.dbnum):
			 db_index[i] = []
		db_index[requested_db].append(real_message)
		current_db = 0
		for i in indexes:
			db_index[current_db].append(self.client.package_message(i, current_db))
			if len(db_index[current_db]) > 2:
				current_db += 1
		return db_index