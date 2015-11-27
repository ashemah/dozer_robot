import argparse
import json
from multiprocessing import Process
from time import sleep
from comms import Comms
from message_bus import MessageBusServer


class RobotCore(object):

    def __init__(self):
        self.launch_order = []
        self.config = None
        self.nodes = {}
        self.running_nodes = {}

    def load_def(self, config_filename):

        print "Config: " + config_filename

        with open(config_filename) as data_file:
            self.config = json.load(data_file)

            self.nodes = self.config['components']

            deps_dict = {}
            for node_name in self.nodes:

                node = self.nodes[node_name]

                if 'launch' in node and node["launch"] == False:
                    continue

                if 'deps' in node:
                    deps = node['deps']
                    deps_dict[node_name] = deps

            self.launch_order = self.resolve_dependencies(deps_dict)

    def launch(self, plugin_dir):

        # Launch message server
        print "Launching: Message Server..."
        message_server = Process(target=self.launch_message_server)
        message_server.start()

        sleep(1)

        for launch_set in self.launch_order:

            for node_name in launch_set:

                node_info = self.nodes[node_name]

                # Now launch the nodes in a new thread
                new_proc = Process(target=self.launch_node, args=(node_name, node_info))
                new_proc.start()

                sleep(0.5)

        print self.running_nodes

    def launch_node(self, node_name, node_info):
        class_name = node_info['classname']

        print "Launching: " + class_name

        cls = self.load_class_by_name(class_name)

        # Instantiate the class

        if 'params' in node_info:
            params = node_info['params']
        else:
            params = {}

        obj = cls(params)

        self.running_nodes[node_name] = {
            'name': node_name,
            'params': params,
            'node': obj
        }

        obj.setup()
        obj.run()

    def load_class_by_name(self, class_name):

        from importlib import import_module

        path, module_name = class_name.rsplit('.', 1)

        module = import_module(path)
        cls = getattr(module, module_name)

        return cls

    def launch_message_server(self):

        print "Starting message bus server"
        comms = Comms()
        message_bus = MessageBusServer()
        comms.add_module(message_bus)
        print "Message bus server started"

        comms.process_messages()

    @classmethod
    def resolve_dependencies(cls, deps_dict):

        '''
            Dependency resolver
            "arg" is a dependency dictionary in which the values are the dependencies of their respective keys.
        '''

        d = dict((k, set(deps_dict[k])) for k in deps_dict)

        r = []

        while d:
            # values not in keys (items without dep)
            t = set(i for v in d.values() for i in v)-set(d.keys())
            # and keys without value (items without dep)
            t.update(k for k, v in d.items() if not v)
            # can be done right away
            r.append(t)
            # and cleaned up
            d = dict(((k, v-t) for k, v in d.items() if v))

        return r

    def run(self):
        pass


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Dozer Core Loader')
    parser.add_argument('-c', action="store", dest='config_filename')
    parser.add_argument('-p', action="store", dest='plugin_dir')
    results = parser.parse_args()

    loader = RobotCore()
    loader.load_def(results.config_filename)
    loader.launch(results.plugin_dir)
