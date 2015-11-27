import subprocess
import psutil
from base_node import BaseNode
from service_link import ServiceClient


class DozerNode(BaseNode):

    def __init__(self, params):
        super(DozerNode, self).__init__(params)

        self.proc = None

        # subscribe
        self.message_bus.subscribe('/rpc/cmd', self.on_rpc_message)

        self.hardware = self.comms.get_service('localhost', 9000, self.on_hardware_message)

        print "Node started"

    def on_hardware_message(self, service_name, message):
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
            self.enable_camera()
        elif method == 'disable_camera':
            self.disable_camera()

    def enable_camera(self):
        if self.proc is not None:
            self.proc.terminate()

        self.proc = subprocess.Popen(["/home/pi/dozer/scripts/video.sh"], stdout=subprocess.PIPE, shell=True)

    def disable_camera(self):

        for proc in psutil.process_iter():
            try:
                pinfo = proc.as_dict(attrs=['pid', 'cmdline'])
            except psutil.NoSuchProcess:
                pass
            else:
                print(pinfo)
                cmdstr = "".join(pinfo['cmdline'])
                if 'video.sh' in cmdstr:
                    parent = psutil.Process(pinfo['pid'])
                    for child in parent.children(recursive=True):  # or parent.children() for recursive=False
                        child.kill()
                    parent.kill()


if __name__ == '__main__':

    dozer_node = DozerNode('/dev/ttyACM0', 9600)
    dozer_node.run()
