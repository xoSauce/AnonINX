import requests
from sphinxmix.SphinxParams import SphinxParams	

class Debug():
	dbg = False

def getGlobalSphinxParams():
	return SphinxParams()

def getPublicIp():

	if Debug.dbg:
		return '0.0.0.0'
	
	_RESPONSE_RETURNED = 200
	link = "http://api.ipify.org?format=json"
	resp = requests.get(link)
	if resp.status_code != _RESPONSE_RETURNED:
		raise Exception("Cannot reach " + link + "to retrieve public ip address")
	return resp.json()["ip"]