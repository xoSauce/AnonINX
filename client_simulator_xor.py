import threading
import time
import subprocess
import random
from functools import reduce
from numpy import median

ip = '54.72.59.68'
times = []
class Runner(threading.Thread):
    def __init__(self, index):
        self.index =index
        threading.Thread.__init__(self)

    def run(self):
        i = self.index
        startTime = time.time()
        response = subprocess.check_call(['python3', '/home/xosauce/UCL/mproject/m_client.py', ip, '-i', str(i), '-db', '0', '-x'], stdout=subprocess.DEVNULL)
        endTime = time.time() - startTime
        times.append(endTime)
        print("Finished with code {}".format(response))

def check_aliveness(threadAlive):
    toRemove = []
    for t in threadAlive:
        if not t.isAlive():
            toRemove.append(t)
    for t in toRemove:
        threadAlive.remove(t)
    print("THERE ARE CURRENTLY {} THREADS ACTIVE".format(len(threadAlive)))

def print_statistics(avg, maximum, minimum, median):
    print("With {} clients with a maximum of {} at any given time was:".format(clients, limit))
    print("AVG {}".format(avg))
    print("MAX {}".format(maximum))
    print("MIN {}".format(minimum))
    print("MEDIAN {}".format(median))

if __name__ == '__main__':
    print("REMEMBER TO SET NEW IP OF BROKER !! Current IP {}".format(ip))
    limit = 50
    clients = 20
    threadAlive = set()
    threadInactive = set()

    for i in range(0, clients):
        threadInactive.add(Runner(random.randint(0, 10)))

    while len(threadInactive) > 0:
        if(len(threadAlive) < limit):
            t = threadInactive.pop()
            t.daemon = True
            t.start()
            threadAlive.add(t)
        check_aliveness(threadAlive)
        print("THREADS LEFT: {}".format(len(threadInactive)))
        time.sleep(0.5)

    while len(times) == 0: time.sleep(0.1)

    avg = reduce(lambda x, y: x + y, times) / len(times)
    min_time = min(times)
    max_time = max(times)
    med = median(times)
    print_statistics(avg, max_time, min_time, med)

    while len(threadAlive) > 0:
        check_aliveness(threadAlive)
        avg = reduce(lambda x, y: x + y, times) / len(times)
        min_time = min(times)
        max_time = max(times)
        med = median(times)
        print_statistics(avg, max_time, min_time, med)
        time.sleep(1)

    avg = reduce(lambda x, y: x + y, times) / len(times)
    min_time = min(times)
    max_time = max(times)
    med = median(times)
    print_statistics(avg, max_time, min_time, med)
    print("Exiting... \n {}".format(times))
