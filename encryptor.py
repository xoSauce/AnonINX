from sphinxmix.SphinxParams import SphinxParams
from sphinxmix.SphinxClient import pki_entry
from binascii import hexlify
from petlib.cipher import Cipher
from os import urandom
from hashlib import sha256

# def keyGenerate(params):
# 	#This getIp() potentially needs to be reworked
# 	ip = self.getIp().encode()
# 	x = params.group.gensecret()
# 	y = params.group.expon(params.group.g, x)
# 	private_key = pki_entry(ip, x, y)
# 	public_key = pki_entry(ip, None, y)
# 	self.private_key = private_key
# 	self.public_key = public_key

class Encryptor():
	
	def __init__(self, group):
		self.G = group
		pass

	def keyGenerate(self, name):
		x = self.G.gensecret()
		y = self.G.expon(self.G.g, x)
		private_key = pki_entry(name, x, y)
		public_key = pki_entry(name, None, y)
		return (public_key, private_key)

	def encrypt_aes_gcm(self, msg, public_key, session):
		aes = Cipher.aes_128_gcm() 
		iv = urandom(16)
		_, aes_private_key = self.keyGenerate(session) 
		x = aes_private_key[1]
		g_x = aes_private_key[2]
		e_key = hexlify(self.G.expon(public_key, x).export())
		e_key = sha256(e_key).digest()[:16]
		ciphertext, tag = aes.quick_gcm_enc(e_key, iv, msg)
		return (g_x, iv, ciphertext, tag)

	def decrypt_aes_gcm(self, msg, secret):
		aes = Cipher.aes_128_gcm()
		g_x, iv, ciphertext, tag = msg
		d_key = hexlify(self.G.expon(g_x, secret).export())
		d_key = sha256(d_key).digest()[:16]
		print("DECRYPT: ", d_key, ciphertext)
		msg = aes.quick_gcm_dec(d_key, iv, ciphertext, tag)
		return msg

if __name__ == '__main__':
	encryptor = Encryptor()