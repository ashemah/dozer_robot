from base_node import BaseNode
from service_link import ServiceServer


class BaseService(BaseNode):

    def __init__(self, node_name, launch_params):
        super(BaseService, self).__init__(node_name, launch_params)
        self.service_host = ServiceServer(self.comms.context, self.get_param('connection_string'), self.on_service_message)
        self.comms.add_module(self.service_host)

    def on_service_message(self, sender, message):
        pass
