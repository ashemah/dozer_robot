import zmq
from message_bus import MessageBusClient
from service_link import ServiceClient


class Comms(object):

    def __init__(self):

        self.registered_modules = []
        self.poller = zmq.Poller()

    def get_message_bus(self):
        message_bus_client = MessageBusClient()
        self.add_module(message_bus_client)
        return message_bus_client

    def get_service(self, service_host, service_port, message_cb):
        service_client = ServiceClient(service_host, service_port, message_cb)
        self.add_module(service_client)
        return service_client

    def add_module(self, module):

        socket = module.get_socket()
        self.registered_modules.append(module)
        self.poller.register(socket)

    def process_messages(self):

        while True:
            socks = dict(self.poller.poll())

            for module in self.registered_modules:
                socket = module.get_socket()

                if socket in socks and socks[socket] == zmq.POLLIN:
                    module.process_socket(socket)

