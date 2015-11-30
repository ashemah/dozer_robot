from comms import Comms


class BaseNode(object):

    def __init__(self, node_name, launch_params):
        self.node_name = node_name
        self.params = launch_params

        self.comms = Comms()
        self.comms.connect_to_master_socket()

        self.message_bus = self.comms.get_message_bus()

    def get_param(self, param_name, default=None):

        if param_name in self.params:
            return self.params[param_name]
        else:
            return default

    def setup(self):
        pass

    def run(self):
        self.comms.process_messages()
