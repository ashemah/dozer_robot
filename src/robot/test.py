from time import sleep
from control_node import RPCProxyNode
from dozer_core import DozerNode
from message_server import MessageBusServer, MessageBusClient
from multiprocessing import Process


def on_message(channel, message):
    print channel
    print message


def run_server():
    server = MessageBusServer()
    server.run()


def run_client():
    node = DozerNode(None)
    node.run()


def run_client2():
    node = RPCProxyNode()
    node.run()


if __name__ == '__main__':

    p1 = Process(target=run_server)
    p1.start()

    sleep(1)

    p2 = Process(target=run_client)
    p2.start()

    sleep(1)

    p3 = Process(target=run_client2)
    p3.start()

    p1.join()
    p2.join()
    p3.join()
