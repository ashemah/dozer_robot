import subprocess
import psutil
from base_service import BaseService


class CameraService(BaseService):

    def __init__(self, node_name, launch_params):
        super(CameraService, self).__init__(node_name, launch_params)
        self.proc = None

    def on_service_message(self, sender, message):

        if 'set_camera_enabled' in message:

            if message['set_camera_enabled']:
                self.enable_camera()
            else:
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
