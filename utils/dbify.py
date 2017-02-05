import argparse
import json
import os
def parse():
	parser = argparse.ArgumentParser()
	parser.add_argument('dbpath', help="database file to dbify")
	args = parser.parse_args()
	return args

def main():
	arguments = vars(parse())
	path = arguments['dbpath']
	f = open(path, 'r')
	records = json.load(f)
	max_len = 0
	for entry in records['collection']:
		max_len = max(len(entry), max_len)
	
	new_records = []
	for entry in records['collection']:
		aux = entry
		while len(aux) < max_len:
			aux += '\n'
		new_records.append(aux)

	json_dict = {'collection': new_records}

	entry_0 = len(json_dict['collection'][0])
	for entry in json_dict['collection']:
		assert(len(entry) == entry_0)

	w = open(path+'_even', 'w')
	w.write(json.dumps(json_dict))

	

if __name__ == '__main__':
	main()