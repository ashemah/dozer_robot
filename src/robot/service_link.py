from uuid import uuid4
import zmq
from zmq.backend.cython.socket import ZMQError
from comms_module_base import CommsModuleBase


class ServiceServer(CommsModuleBase):

    def __init__(self, zmq_context, connection_string, command_cb):

        self.context = zmq_context

        self.command_cb = command_cb

        self.connected_clients = {}
        self.active_commands = {}

        self.recv_socket = self.context.socket(zmq.REP)
        print "Service Host running on {}".format(connection_string)
        self.recv_socket.bind(connection_string)

    def get_socket(self):
        return self.recv_socket

    def process_socket(self, socket):

        print "Processing service message..."

        msg_json = self.recv_socket.recv_json()

        print "Service received: " + str(msg_json)

        msg_type = msg_json['type']
        sender = msg_json['sender']

        if msg_type == 'connect':
            self.connected_clients[sender] = {'status': 'connected'}
            self.recv_socket.send_json({'status': 'ok'})

        elif msg_type == 'disconnect':
            del self.connected_clients[sender]
            self.recv_socket.send_json({'status': 'ok'})

        elif msg_type == 'cmd':
            print "Service Command: " + str(msg_json)

            cmd = msg_json['cmd']
            cmd_key = msg_json['cmd_key']

            if cmd_key in self.active_commands:
                self.remove_command(cmd_key)

            self.active_commands[cmd_key] = {
                'sender': sender,
                'cmd_key': cmd_key,
                'cmd': cmd
            }

            self.command_cb(sender, cmd)
            self.recv_socket.send_json({'status': 'ok'})

        elif msg_type == 'abort':
            print "Abort Command: " + str(msg_json)

            cmd = msg_json['cmd']
            cmd_key = msg_json['cmd_key']

            if cmd_key in self.active_commands:
                self.remove_command(cmd_key)

            self.recv_socket.send_json({'status': 'ok'})

    def remove_command(self, cmd_key):
        if cmd_key in self.active_commands:
            del self.active_commands[cmd_key]


class ServiceClient(CommsModuleBase):

    def __init__(self, zmq_context, connection_string, cmd_cb):

        self.is_connected = False

        self.connection_string = connection_string

        self.context = zmq_context
        self.sender = str(uuid4())

        self.cmd_cb = cmd_cb

        self.send_socket = self.context.socket(zmq.REQ)
        self.connect()

    def get_socket(self):
        return self.send_socket

    def process_socket(self, socket):
        pass

    def connect(self):

        self.send_socket.connect(self.connection_string)

        try:
            self.send_socket.send_json({'type': 'connect', 'sender': self.sender}, zmq.NOBLOCK)
            res = self.send_socket.recv_json()

            self.is_connected = True

        except ZMQError, e:
            self.is_connected = False

    def send(self, command, cmd_key=''):

        if self.is_connected:
            print "Sending: {}".format(command)
            self.send_socket.send_json({'type': 'cmd', 'sender': self.sender, 'cmd': command, 'cmd_key': cmd_key})
            res = self.send_socket.recv_json()
        else:
            print "Dropping send as is not connected"
