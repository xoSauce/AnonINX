import argparse
import json
import os
from binascii import hexlify, unhexlify
from sphinxmix.SphinxClient import Nenc
from sphinxmix.SphinxClient import rand_subset, create_forward_message, create_surb, receive_surb
from request_creator import RequestCreator, RequestType, PortEnum, PortEnumDebug
from network_sender import NetworkSender
from epspvt_utils import getGlobalSphinxParams, Debug, getPublicIp
from petlib.ec import EcPt
from logger import log_init, log_debug
from broker_communicator import BrokerCommunicator
from encryptor import Encryptor
from petlib.pack import encode, decode
from client_poller import ClientPoller
from pir_executor import PIRExecutor
from message_creator import MessageCreator


class Client:
    def __init__(self, public_key_server):
        self.broker_comm = BrokerCommunicator()
        self.public_key_server = public_key_server
        self.db_list = None
        self.mixnode_list = None
        self.ip = getPublicIp()
        self.encryptor = Encryptor(getGlobalSphinxParams().group)
        self.surbDict = {}

    def encryptForDB(self, msg, key, session_name):
        getGlobalSphinxParams().group
        g_x, iv, ciphertext, tag = self.encryptor.encrypt_aes_gcm(
            msg, key, session_name
        )
        e_message = {
            'pk': hexlify(g_x.export()).decode('utf-8'), 'iv': hexlify(iv).decode('utf-8'), 'text': hexlify(ciphertext).decode('utf-8'), 'tag': hexlify(tag).decode('utf-8')
        }
        json_msg = json.dumps(e_message, ensure_ascii=False)
        return (json_msg)

    def getDBRecordSize(self, portEnum, network_sender):
        session_name = os.urandom(16)
        self.public_key, self.private_key = self.encryptor.keyGenerate(
            session_name)
        db_dest, key = self.create_db_destination(0, portEnum.db.value)
        message = encode(self.create_db_message(None, {
                         'pir_xor': None, 'request_type': RequestType.get_db_size.value, 'pk': self.public_key}))
        json_msg = self.encryptForDB(message, key, session_name)
        response = network_sender.send_data_wait(
            json_msg, {'ip': db_dest[0], 'port': db_dest[2]})
        return int.from_bytes(response, 'big')

    def xor(self, messages):
        pir_executor = PIRExecutor()
        message = messages[0]
        for m in messages[1:]:
            message = pir_executor.stringXorer(message, m)
        return message.decode().strip()

    def decrypt(self, cipher, private_key):
        iv = cipher['iv']
        text = cipher['text']
        pk = cipher['pk']
        tag = cipher['tag']
        msg = self.encryptor.decrypt_aes_gcm((pk, iv, text, tag), private_key)
        return msg

    def poll_recordSize(self, DummyIndex):
        self.client_poller = ClientPoller()
        messages = {}
        threads = []
        for surbid, data in self.surbDict.items():
            threads.append(self.client_poller.poll_with(
                (surbid, data['source']), self, messages))
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        # First one is the record size
        surbid = list(self.surbDict.keys())[0]
        self.surbDict = {}
        record_size = decode(self.decrypt(
            messages[surbid][1], self.private_key[1]))
        return record_size

    def poll_index(self, pir, requested_index):
        self.client_poller = ClientPoller()
        threads = []
        messages = {}
        for surbid, data in self.surbDict.items():
            threads.append(self.client_poller.poll_with(
                (surbid, data['source']), self, messages))
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        decrypted_msgs = []
        if not pir:
            decrypted_msgs = {}
        try:
            for surbid, _ in self.surbDict.items():
                msg = self.surbDict[surbid]
                log_debug(msg)
                decrypted_msg = decode(self.decrypt(
                    messages[surbid][1], msg['key'][1]))
                if pir:
                    decrypted_msgs.append(decrypted_msg)
                else:
                    decrypted_msgs[messages[surbid][0]] = decrypted_msg
            if pir:
                return self.xor(decrypted_msgs)
            else:
                return decrypted_msgs[requested_index].strip()
        except Exception as e:
            print(e)
            log_debug('[ERROR] Exception\n{}\n'.format(e))

    def recoverMessage(self, msg, myid):
        surbkeytuple = self.surbDict[myid]['surbkeytuple']
        index = self.surbDict[myid]['index']
        return (index, decode(receive_surb(getGlobalSphinxParams(), surbkeytuple, msg)))

    def populate_broker_lists(self, source=None):
        if source == None:
            source = self.public_key_server

        def unhexlify_values(a_dict):
            for x in a_dict.keys():
                a_dict[x] = unhexlify(a_dict[x])
            return a_dict

        def get_db_list(source, client):
            dbs_dict_raw = client.broker_comm.getDBList({
                'ip': source['ip'],
                'port': source['port']
            })
            dbs_dict_raw = unhexlify_values(dbs_dict_raw)
            dbs_dict = {}
            for index, (key, value) in enumerate(dbs_dict_raw.items()):
                dbs_dict[index] = (key, value)
            return dbs_dict

        def get_mixnode_list(source, client):
            mixnodes_dict = client.broker_comm.getMixNodeList({
                'ip': source['ip'],
                'port': source['port']
            })
            mixnodes_dict = unhexlify_values(mixnodes_dict)
            return mixnodes_dict

        self.mixnode_list = get_mixnode_list(source, self)
        self.db_list = get_db_list(source, self)

    def create_db_message(self, index, settings):
        msg = {
            'index': index,
            'pir_xor': settings['pir_xor'],
            'request_type': settings['request_type'],
            'pk': settings['pk'],
            'nymtuple': None
        }
        return msg

    def create_db_destination(self, destination, port):
        try:
            destination = self.db_list[destination]
            destination = (destination[0], destination[1], port)
            key = EcPt.from_binary(
                destination[1], getGlobalSphinxParams().group.G)
            return (destination, key)
        except Exception as e:
            raise Exception(
                'Requested database not present or named incorrectly. {} not found'.format(destination))

    def package_message(self, index, db, pir_xor, portEnum, request_type=RequestType.push_to_db.value, mix_subset=5, session_name=None):

        self.public_key, self.private_key = self.encryptor.keyGenerate(
            session_name)
        self.session_name = session_name

        def json_encode(arguments):
            return json.dumps(dict(arguments))

        def prepare_forward_message(mixnodes_dict, message, dest, key, portEnum):
            params = getGlobalSphinxParams()
            group = params.group.G
            use_nodes_forward = rand_subset(mixnodes_dict.keys(), 5)
            use_nodes_backward = rand_subset(mixnodes_dict.keys(), 5)
            nodes_routing_forward = list(map(Nenc, use_nodes_forward))
            nodes_routing_backward = list(map(Nenc, use_nodes_backward))
            pks_chosen_nodes_forward = [
                EcPt.from_binary(mixnodes_dict[key], group)
                for key in use_nodes_forward
            ]
            pks_chosen_nodes_backward = [
                EcPt.from_binary(mixnodes_dict[key], group)
                for key in use_nodes_backward
            ]
            surbid, surbkeytuple, nymtuple = create_surb(
                params,
                nodes_routing_backward,
                pks_chosen_nodes_backward,
                self.ip)
            self.surbDict[surbid] = {'surbkeytuple': surbkeytuple}
            message['nymtuple'] = nymtuple
            message = encode(message)
            json_msg = self.encryptForDB(message, key, self.session_name)
            header, delta = create_forward_message(params,
                                                   nodes_routing_forward,
                                                   pks_chosen_nodes_forward,
                                                   dest,
                                                   json_msg)
            return (header, delta, use_nodes_forward[0], surbid, use_nodes_backward[-1])

        if len(self.mixnode_list) == 0:
            print("There are no mix-nodes available.")
            return

        if len(self.db_list) == 0:
            print("There are no databases available.")
            return
        db_dest, key = self.create_db_destination(db, portEnum.db.value)
        message = self.create_db_message(
            index, {'pir_xor': pir_xor, 'request_type': request_type, 'pk': self.public_key})
        header, delta, first_mix, surbid, mix_to_poll = prepare_forward_message(self.mixnode_list,
                                                                                message,
                                                                                db_dest,
                                                                                key,
                                                                                portEnum)
        self.surbDict[surbid]['index'] = index
        self.surbDict[surbid]['source'] = mix_to_poll
        self.surbDict[surbid]['key'] = self.private_key
        json_data, dest = RequestCreator().post_msg_to_mix(
            {'ip': first_mix, 'port': portEnum.mix.value},
            {'header': header, 'delta': delta}
        )
        if Debug.dbg is True:
            dest['ip'] = b'0.0.0.0'
        return (json_data, dest)


def parse():
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--debug', action="store_true",
                        help="Debug Mode -- to be able to connect to own computer via local ip (skip public ip connection)")
    parser.add_argument('-x', '--xor', action="store_true",
                        help="Use vector xoring method")
    parser.add_argument(
        'pkserver', help="Specify the public IP address of the server where public keys will be stored.")
    parser.add_argument(
        'port', help="Specify the port where the server is listening for connections")
    parser.add_argument('-i', '--requested_index',
                        help="Specify the index to retrieve")
    parser.add_argument(
        '-db', '--database', help="Specify the number of the datbase in the range[0-?]")
    args = parser.parse_args()
    return args


def main():
    log_init("m_client.log")
    args = vars(parse())
    portEnum = PortEnum
    if args['debug']:
        Debug.dbg = True
        portEnum = PortEnumDebug

    client = Client({
        'ip': args['pkserver'],
        'port': portEnum.broker.value
    })
    client.populate_broker_lists()
    index = int(args['requested_index'])
    db = int(args['database'])
    requested_index, requested_db = (index, db)
    messageCreator = MessageCreator(client)
    network_sender = NetworkSender()
    record_size = client.getDBRecordSize(portEnum, network_sender)
    if args['xor']:
        messages = messageCreator.generate_messages(
            requested_index, requested_db, record_size, portEnum, pir_xor=True)
    else:
        messages = messageCreator.generate_messages(
            requested_index, requested_db, record_size, portEnum, pir_xor=False)
    for db in messages:
        [network_sender.send_data(json, dest) for json, dest in messages[db]]
    print("POLL_INDEX RESULT:", client.poll_index(
        args['xor'], requested_index), "REQUESTED_INDEX", requested_index)


if __name__ == '__main__':
    main()
