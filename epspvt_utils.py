import requests
from sphinxmix.SphinxParams import SphinxParams	
#
def getGlobalSphinxParams():
	return SphinxParams()

def getPublicIp():
	_RESPONSE_RETURNED = 200
	link = "https://api.ipify.org?format=json"
	resp = requests.get(link)
	if resp.status_code != _RESPONSE_RETURNED:
		raise Exception("Cannot reach " + link + "to retrieve public ip address")
	return resp.json()["ip"]