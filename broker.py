import threading
from binascii import unhexlify

class Broker():
    def __init__(self):
        self.mix_public_keys = {}
        self.db_public_keys = {}
        self.lock = threading.Lock()

    ### takes type='mix' or type='db'
    def fetch(self, data, m_type):
        self.lock.acquire()
        if m_type == 'mix':
            where_from = self.mix_public_keys
        else:
            where_from = self.db_public_keys

        try:
            if data == []:
                return where_from
            else:
                return dict([x for x in map(self.get_cache_entry, data, where_from)])
        finally:
            self.lock.release()

    def register(self, data, m_type):
        self.lock.acquire()
        try:
            public_key_name = 'pk'
            id_name = 'id'
            if public_key_name in data and id_name in data:
                data[id_name] = data[id_name]
                if m_type == 'mix':
                    self.mix_public_keys.update({data[id_name]:data[public_key_name]})
                elif m_type == 'db':
                    self.db_public_keys.update({data[id_name]:data[public_key_name]})
        finally:
            self.lock.release()


    def get_cache_entry(self, data, where_from):
        if data['id'] in where_from:
            return (data['id'], where_from[data['id']])
        else:
            raise ValueError('Requested id: %s was not made public' % data['id'])
