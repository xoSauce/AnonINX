import requests
import sys
import linecache
from sphinxmix.SphinxParams import SphinxParams

class Debug():
    dbg = False

class ProtocolNumber():
    PROTOCOL_BYTE_NUMBER = 15

class SecurityParameters():
    NUMBER_OF_REQUESTS = 16 # p in the paper
    REQUESTS_IN_THE_POOL = 3
    SPARSITY_FACTOR = 0.3
    NUMBER_OF_MIXES = 5 ##selection of number of mixes
    # theta sparsity factor
    # corrupt databases
    #

def getGlobalSphinxParams():
    return SphinxParams(header_len = 500, body_len=4096*50)

def PrintException():
    exc_type, exc_obj, tb = sys.exc_info()
    f = tb.tb_frame
    lineno = tb.tb_lineno
    filename = f.f_code.co_filename
    linecache.checkcache(filename)
    line = linecache.getline(filename, lineno, f.f_globals)
    print ('EXCEPTION IN ({}, LINE {} "{}"): {}'.format(filename, lineno, line.strip(), exc_obj))



def getPublicIp():

    if Debug.dbg:
        return '0.0.0.0'

    _RESPONSE_RETURNED = 200
    link = "http://api.ipify.org?format=json"
    resp = requests.get(link)
    if resp.status_code != _RESPONSE_RETURNED:
        raise Exception("Cannot reach " + link + "to retrieve public ip address")
    return resp.json()["ip"]
