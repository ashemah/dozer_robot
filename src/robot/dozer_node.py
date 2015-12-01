from base_node import BaseNode


class DozerNode(BaseNode):

    def __init__(self, namespace, node_name, launch_params):
        super(DozerNode, self).__init__(namespace, node_name, launch_params)

        # subscribe
        self.message_bus.subscribe('/rpc/cmd', self.on_rpc_message)

        self.hardware = self.comms.get_service('hardware_service', self.on_hardware_message)
        self.camera = self.comms.get_service('camera_service', self.on_camera_message)
        self.speech = self.comms.get_service('speech_service', self.on_speech_message)

        self.say("Dozer is online")

    def say(self, text):
        print "Say: {}".format(text)
        self.speech.send({'cmd': 'say', 'text': text})

    def on_speech_message(self, service_name, message):
        pass

    def on_hardware_message(self, service_name, message):
        pass

    def on_camera_message(self, service_name, message):
        pass

    def on_rpc_message(self, channel, message):

        method = message['method']

        if method == 'move_fwd':
            self.hardware.send({'cmd': 'fwd'})
        elif method == 'move_back':
            self.hardware.send({'cmd': 'back'})
        elif method == 'rotate_left':
            self.hardware.send({'cmd': 'left'})
        elif method == 'rotate_right':
            self.hardware.send({'cmd': 'right'})
        elif method == 'stop':
            self.hardware.send({'cmd': 'stop'})
        elif method == 'slider_changed':
            value = message['value']
            self.hardware.send({'cmd': 'move_head', 'position': value})
        elif method == 'enable_camera':
            self.camera.send({'set_camera_enabled': True})
        elif method == 'disable_camera':
            self.camera.send({'set_camera_enabled': False})

if __name__ == '__main__':

    dozer_node = DozerNode('/dev/ttyACM0', 9600, {})
    dozer_node.run()
