import sys, os
myPath = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, myPath + '/../')
print (myPath)
from encryptor import Encryptor
from sphinxmix.SphinxParams import SphinxParams
from binascii import hexlify

def test_encryptor_encrypt_decrypt():
	params = SphinxParams()
	group = params.group
	encryptor = Encryptor(group)
	msg = hexlify(str(2).encode())
	session_name = os.urandom(16)
	## Alice
	pk, sk = encryptor.keyGenerate('test')
	## Bob
	public_key_expon, iv, ciphertext, tag = encryptor.encrypt_aes_gcm(msg, pk[2], session_name)
	## Alice
	msg_decrypted = encryptor.decrypt_aes_gcm(
		(public_key_expon, iv, ciphertext, tag), 
		sk[1])
	assert(msg_decrypted == msg)