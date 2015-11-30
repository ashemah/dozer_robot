import zmq
from message_bus import MessageBusClient
from service_link import ServiceClient


class Comms(object):

    def __init__(self, is_client=True):

        self.context = zmq.Context()

        self.registered_modules = []
        self.poller = zmq.Poller()

        self.master_socket_cb = None

        if is_client:
            self.connect_to_master_socket()
        else:
            self.bind_master_socket()

    def set_master_socket_cb(self, cb):
        self.master_socket_cb = cb

    def connect_to_master_socket(self):
        self.master_socket = self.context.socket(zmq.REQ)
        self.master_socket.connect("ipc:///tmp/master")

    def bind_master_socket(self):
        self.master_socket = self.context.socket(zmq.REP)
        self.master_socket.bind("ipc:///tmp/master")
        self.poller.register(self.master_socket)

    def get_connection_string_for_service(self, service_name):
        self.master_socket.send_json({'cmd': 'resolve_service', 'service_name': service_name})
        res = self.master_socket.recv_json()
        return res['connection_string']

    def get_message_bus(self):
        message_bus_client = MessageBusClient(self.context)
        self.add_module(message_bus_client)
        return message_bus_client

    def get_service(self, service_name, message_cb):
        connection_string = self.get_connection_string_for_service(service_name)
        service_client = ServiceClient(self.context, connection_string, message_cb)
        self.add_module(service_client)
        return service_client

    def add_module(self, module):
        socket = module.get_socket()
        self.registered_modules.append(module)
        self.poller.register(socket)

    def process_master_socket_message(self, socket):

        message = socket.recv_json()
        res = self.master_socket_cb(message)
        socket.send_json(res)

    def process_messages(self):

        while True:
            socks = dict(self.poller.poll())

            if self.master_socket in socks and socks[self.master_socket] == zmq.POLLIN:
                # Process master socket
                self.process_master_socket_message(self.master_socket)

            else:

                for module in self.registered_modules:
                    socket = module.get_socket()

                    if socket in socks and socks[socket] == zmq.POLLIN:
                        module.process_socket(socket)

