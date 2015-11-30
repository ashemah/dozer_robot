from uuid import uuid4
import zmq
from comms_module_base import CommsModuleBase


class MessageBusServer(CommsModuleBase):

    def __init__(self, zmq_context, bus_socket='9111', publish_socket='9112'):

        self.context = zmq_context

        self.bus_socket = self.context.socket(zmq.REP)
        self.pub_socket = self.context.socket(zmq.PUB)

        self.subscribed_channels = {}

        self.bus_socket.bind("tcp://*:{}".format(publish_socket))
        self.pub_socket.bind("tcp://*:{}".format(bus_socket))

    def get_socket(self):
        return self.bus_socket

    def process_socket(self, socket):
        msg_json = socket.recv_json()

        print "Received: " + str(msg_json)

        msg_type = msg_json['type']
        msg_sender = msg_json['sender']

        if msg_type == 'subscribe':
            print "Subscribed"
            msg_channel = msg_json['channel']

            if msg_channel in self.subscribed_channels:
                subscriber_list = self.subscribed_channels[msg_channel]
                subscriber_list.append(msg_sender)
            else:
                subscriber_list = [msg_sender]

            self.subscribed_channels[msg_channel] = subscriber_list

        elif msg_type == 'unsubscribe':
            pass
            # Remove the subscriber here
        elif msg_type == 'publish':
            print "Publishing: " + str(msg_json)
            self.pub_socket.send_json(msg_json)

        socket.send_json({})


class MessageBusClient(CommsModuleBase):

    def __init__(self, zmq_context, bus_socket='tcp://localhost:9111', publish_socket='tcp://localhost:9112'):

        self.context = zmq_context

        self.uuid = str(uuid4())

        self.pub_socket = self.context.socket(zmq.REQ)

        self.sub_socket = self.context.socket(zmq.SUB)
        self.sub_socket.setsockopt(zmq.SUBSCRIBE, "")

        self.subscriptions = {}
        self.connected_services = []

        self.pub_socket.connect(publish_socket)
        self.sub_socket.connect(bus_socket)

    def get_socket(self):
        return self.sub_socket

    def process_socket(self, socket):
        msg_json = socket.recv_json()

        msg_channel = msg_json['channel']

        print "Subscriptions " + str(self.subscriptions)

        if msg_channel in self.subscriptions:
            print "Subscriber Recvd: " + str(msg_json)
            msg_payload = msg_json['message']

            callback = self.subscriptions[msg_channel]
            callback(msg_channel, msg_payload)

    def subscribe(self, channel, callback):
        self.subscriptions[channel] = callback

        self.pub_socket.send_json({
            'type': 'subscribe',
            'sender': self.uuid,
            'channel': channel
        })

        res = self.pub_socket.recv_json()

    def publish(self, channel, message):
        print "Publishing message: " + str(message)

        self.pub_socket.send_json({
            'type': 'publish',
            'sender': self.uuid,
            'channel': channel,
            'message': message
        })

        res = self.pub_socket.recv_json()
