from broker import Broker
from key_listener import KeyListener
from request_creator import PortEnum
from threading import Thread
import asyncore
import subprocess as sp
import time
class StatusChecker(Thread):
    def __init__(self,broker):
        Thread.__init__(self)
        self.broker = broker

    def isAlive(self, ip):
        status,result = sp.getstatusoutput("ping -c1 -w2 " + str(ip))
        if status == 0:
            return 1

    def delete_unresponse_mixes(self):
        broker = self.broker
        remove_mix = []
        remove_db = []
        for entry in broker.mix_public_keys:
            if not self.isAlive(entry):
                remove_mix.append(entry)

        for entry in broker.db_public_keys:
            if not self.isAlive(entry):
                remove_db.append(entry)

        for entry in remove_mix:
            del broker.mix_public_keys[entry]

        for entry in remove_db:
            del broker.db_public_keys[entry]
        # print("Mixnodes", broker.mix_public_keys)
        # print("Dbs", broker.db_public_keys)

    def kill(self):
        self.work = False

    def run(self):
        self.work = True
        while self.work:
            # self.delete_unresponse_mixes()
            time.sleep(5)

def main():
    portEnum = PortEnum
    broker = Broker()
    status = StatusChecker(broker)
    try:
        status.start()
        KeyListener('0.0.0.0', portEnum.broker.value, broker)
        loop_thread = Thread(target=asyncore.loop, name="Asyncore Loop")
        loop_thread.start()
    except Exception as e:
        print(e)
        status.kill()


if __name__ == '__main__':
    main()
