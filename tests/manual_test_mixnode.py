def test_mix_single_message():
	from sphinxmix.SphinxParams import SphinxParams
	from sphinxmix.SphinxClient import pki_entry, Nenc
	from sphinxmix.SphinxClient import rand_subset, create_forward_message
	from sphinxmix.SphinxClient import receive_forward
	from network_sender import NetworkSender
	params = SphinxParams()
	pkiPub = {}
	for i in range(10):
	    nid = i
	    x = params.group.gensecret()
	    y = params.group.expon(params.group.g, x)
	    pkiPub[nid] = pki_entry(nid, None, y)

	use_nodes = rand_subset(pkiPub.keys(), 5)
	nodes_routing = list(map(Nenc, use_nodes))
	keys_nodes = [pkiPub[n].y for n in use_nodes]
	dest = b"bob"
	message = b"this is a test"
	header, delta =  create_forward_message(params, 
		nodes_routing, 
		keys_nodes, 
		dest, 
		message)
	from netwo