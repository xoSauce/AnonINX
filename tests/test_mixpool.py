import sys, os
myPath = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, myPath + '/../')

from mix_pool import MixPool

def test_mixpool_selection():
	minsize = 3
	mixpool = MixPool(minsize)
	mixpool.pool = [1,2,3,4,5,6,7,8,9,10]
	selection = mixpool.getSelection()
	assert(len(selection) == minsize)
	assert(len(mixpool.pool) == 7)
	selection = mixpool.getSelection()
	assert(len(selection) == minsize)
	assert(len(mixpool.pool) == 4)
	selection = mixpool.getSelection()
	assert(len(selection) == 1)
	assert(len(mixpool.pool) == 3)
	## one more selection would block.
