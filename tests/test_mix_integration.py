import sys, os
myPath = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, myPath + '/../')

# def test_mix_single_message():
# 	from sphinxmix.SphinxParams import SphinxParams
# 	from sphinxmix.SphinxClient import pki_entry, Nenc
# 	from sphinxmix.SphinxClient import rand_subset, create_forward_message
# 	from sphinxmix.SphinxClient import receive_forward
# 	import mix
# 	params = SphinxParams()
# 	pkiPub = {}
# 	for i in range(10):
# 	    nid = i
# 	    x = params.group.gensecret()
# 	    y = params.group.expon(params.group.g, x)
# 	    pkiPub[nid] = pki_entry(nid, None, y)

# 	use_nodes = rand_subset(pkiPub.keys(), 5)
# 	nodes_routing = list(map(Nenc, use_nodes))
# 	keys_nodes = [pkiPub[n].y for n in use_nodes]
# 	dest = b"bob"
# 	message = b"this is a test"
# 	header, delta =  create_forward_message(params, 
# 		nodes_routing, 
# 		keys_nodes, 
# 		dest, 
# 		message)

# 	import threading
# 	waiter_called = threading.Event();
# 	m_mix = mix.MixNode()

# 	def waiter():
# 		assert  m_mix.getDecodedResult()== [dest, message]
# 		waiter_called.set()

	
# 	import time
# 	t = threading.Thread(target=m_mix.run, args=(header,delta), kwargs={'cb':waiter})
# 	t.start()
# 	while not waiter_called.wait(timeout = 1):
# 		assert False
	
