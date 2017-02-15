from broker import Broker
from key_listener import KeyListener
from requestCreator import PortEnum
def main():
	portEnum = PortEnum
    broker = Broker()
    key_listener = KeyListener(portEnum.broker.value, broker)
    key_listener.listen()

if __name__ == '__main__':
    main()