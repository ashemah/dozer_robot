import argparse
import json
from multiprocessing import Process
from time import sleep
import redis
from comms import Comms
from message_bus import MessageBusServer


class RobotCore(object):

    def __init__(self):
        self.launch_order = []
        self.config = None
        self.components = {}
        self.connection_strings = {}
        self.running_nodes = {}

        self.comms = Comms('/master')
        self.comms._bind_master_socket()
        self.comms._set_master_socket_cb(self.handle_master_socket_message)

        self.redis = redis.StrictRedis(host='localhost', port=6379, db=0)

    def handle_master_socket_message(self, message):

        if message['cmd'] == 'resolve_service':

            service_name = message['service_name']
            connection_string = self.connection_strings[service_name]

            res = {
                'service_name': service_name,
                'connection_string': connection_string
            }

            return res

        elif message['cmd'] == 'set_param':
            param_name = message['name']
            param_value = message['value']
            self.redis.set(param_name, param_value)
            return {'status': 'success'}

        elif message['cmd'] == 'get_param':
            param_name = message['name']
            return self.redis.get(param_name)

    def load_definition(self, config_filename):

        print "Config: " + config_filename

        with open(config_filename) as data_file:
            self.config = json.load(data_file)

            self.components = {}
            deps_dict = {}

            last_name = None

            # load from the nodes
            if 'nodes' in self.config:
                nodes = self.config['nodes']
                for node_name in nodes:

                    node = nodes[node_name]
                    self.components[node_name] = node

                    if 'launch' in node and node["launch"] == False:
                        continue

                    if 'dependencies' in node:
                        deps = node['dependencies']
                        deps_dict[node_name] = deps

                    last_name = node_name

            if 'services' in self.config:
                # load from the services
                services = self.config['services']
                for node_name in services:

                    node = services[node_name]
                    self.components[node_name] = node

                    if 'launch' in node and node["launch"] == False:
                        continue

                    if 'deps' in node:
                        deps = node['deps']
                        deps_dict[node_name] = deps

                    last_name = node_name

            # Build the load order
            self.launch_order = self.resolve_dependencies(deps_dict)

            if len(self.launch_order) == 0:
                self.launch_order.append((last_name,))

            print "Launch order: {}".format(self.launch_order)

    def launch(self, plugin_dir):

        # Launch message server
        print "Node: Message Server..."
        message_bus_server = MessageBusServer(self.comms.context)
        self.comms.add_module(message_bus_server)

        sleep(0.5)

        for launch_set in self.launch_order:

            for node_name in launch_set:

                node_info = self.components[node_name]

                # Instantiate the class
                if 'launch_params' in node_info:
                    launch_params = node_info['launch_params']
                else:
                    launch_params = {}

                launch_service_locally = True

                # Connect to external service
                if 'is_external' in node_info:
                    launch_service_locally = False
                    host = node_info['hostname']
                    port = node_info['port']
                    connection_string = "tcp://{}:{}".format(host, port)

                # Export internal service
                elif 'is_published' in node_info:

                    if 'hostname' in node_info:
                        host = node_info['hostname']
                    else:
                        host = "*"

                    if 'port' in node_info:
                        port = node_info['port']
                    else:
                        port = 9111 # Make this a random port within the range allowed

                    connection_string = "tcp://{}:{}".format(host, port)

                # Standard internal service
                else:
                    connection_string = "ipc:///tmp/{}".format(node_name)

                launch_params['connection_string'] = connection_string
                self.connection_strings[node_name] = connection_string

                namespace = '/components/{}'.format(node_name)

                # Now launch the nodes in a new thread

                if launch_service_locally:

                    # Class name
                    class_name = node_info['class_name']

                    new_proc = Process(target=self.launch_node_async, args=(namespace, node_name, class_name, launch_params))
                    new_proc.start()

                sleep(0.5)

    def on_master_service_message(self):
        pass

    def launch_node_async(self, namespace, node_name, class_name, launch_params):

        print "Node: " + node_name

        cls = self.load_class_by_name(class_name)

        obj = cls(namespace, node_name, launch_params)

        self.running_nodes[node_name] = {
            'name': node_name,
            'launch_params': launch_params,
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
        self.comms.process_messages()


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Dozer Core Loader')
    parser.add_argument('-c', action="store", dest='config_filename')
    parser.add_argument('-p', action="store", dest='plugin_dir')
    results = parser.parse_args()

    loader = RobotCore()
    loader.load_definition(results.config_filename)
    loader.launch(results.plugin_dir)
    loader.run()
