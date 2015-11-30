from jsonrpclib.SimpleJSONRPCServer import SimpleJSONRPCServer
from base_node import BaseNode


class RPCProxyNode(BaseNode):

    def __init__(self, node_name, launch_params):
        super(RPCProxyNode, self).__init__(node_name, launch_params)

        self.server = SimpleJSONRPCServer((self.get_param('hostname', "0.0.0.0"), self.get_param('port', 8080)))
        self.server.register_instance(self)
        self.server.register_function(self.move_fwd)
        self.server.register_function(self.move_back)
        self.server.register_function(self.rotate_left)
        self.server.register_function(self.rotate_right)
        self.server.register_function(self.stop)
        self.server.register_function(self.slider_changed)
        self.server.register_function(self.enable_camera)
        self.server.register_function(self.disable_camera)

    # def _dispatch(self, name, params):
    #     self.message_bus.publish('/control/cmd', {'name': name, params: params})

    def move_fwd(self):
        self.message_bus.publish('/rpc/cmd', {'method': 'move_fwd'})

    def move_back(self):
        self.message_bus.publish('/rpc/cmd', {'method': 'move_back'})

    def rotate_left(self):
        self.message_bus.publish('/rpc/cmd', {'method': 'rotate_left'})

    def rotate_right(self):
        self.message_bus.publish('/rpc/cmd', {'method': 'rotate_right'})

    def stop(self):
        self.message_bus.publish('/rpc/cmd', {'method': 'stop'})

    def slider_changed(self, **kwargs):
        self.message_bus.publish('/rpc/cmd', {'method': 'slider_changed', 'value': kwargs['value']})

    def enable_camera(self):
        self.message_bus.publish('/rpc/cmd', {'method': 'enable_camera'})

    def disable_camera(self):
        self.message_bus.publish('/rpc/cmd', {'method': 'disable_camera'})

    def run(self):
        self.server.serve_forever()
