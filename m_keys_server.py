from broker import Broker
from key_listener import KeyListener
def main():
    broker = Broker()
    key_listener = KeyListener(8080, broker)
    key_listener.listen()

if __name__ == '__main__':
    main()