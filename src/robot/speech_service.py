import subprocess
from base_service import BaseService


class SpeechService(BaseService):

    def __init__(self, namespace, node_name, launch_params):
        super(SpeechService, self).__init__(namespace, node_name, launch_params)

    def on_service_message(self, sender, message):

        cmd = message['cmd']
        text = message['text']

        if cmd == 'say':
            subprocess.Popen(['say', text])

