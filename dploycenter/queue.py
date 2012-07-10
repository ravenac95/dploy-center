import logging
import zmq
import threading
import uuid
from . import constants
from .server import Server

logger = logging.getLogger('dploycenter')

def start_server(context, control_socket_uri, options, config):
    server = DeployQueueServer.create(context, control_socket_uri, options, 
            config)
    server.run()

class DeployDirector(object):
    def __init__(self, *args, **kwargs):
        pass

    def complete_deployment(self):
        pass

def handle_deploy_order(deploy_order, broadcast_descriptor):
    """Spawns the DeployDirector"""
    director = DeployDirector(deploy_order, broadcast_descriptor)
    director.complete_deployment()

class DeployQueueServer(Server):
    """Queues DeployOrders
    
    DeployOrders can be made through one of the following actions:

        1. A user pushes a git repository
        2. A user changes the environment settings
        3. A user changes the required services
        4. The system forces an upgrade of the Cargo's AppContainer Base
    """
    def __init__(self, *args, **kwargs):
        super(DeployQueueServer, self).__init__(*args, **kwargs)
        self.queue = []

    def setup_sockets(self):
        queue_socket_uri = self.config.get(constants.MAIN_CONFIG_SECTION, 
                'queue-socket')
        
        queue_socket = self.context.socket(zmq.REP)
        queue_socket.bind(queue_socket_uri)

        return {
            'queue': queue_socket,
        }

    def handle_queue(self, socket):
        # Receive the raw DeployOrder data
        raw_deploy_order = socket.recv_json()

        # Create a DeployOrder out of the raw data
        deploy_order = DeployOrder.from_dict(raw_deploy_order)

        # Get Broadcasting input uri
        broadcast_in_uri = self.config.get(constants.MAIN_CONFIG_SECTION,
                'broadcast-socket-in')

        # Create a BroadcastDescriptor
        broadcast_descriptor = BroadcastDescriptor.create_random(broadcast_in_uri)

        # Send the listening channel back to the caller
        socket.send_json(broadcast_descriptor.to_listening_dict())

        # Start the worker thread
        thread = threading.Thread(target=handle_deploy_order, 
                args=[deploy_order, broadcast_descriptor])
        thread.start()

class BroadcastDescriptor(object):
    @classmethod
    def create_random(cls, uri, prefix=''):
        """Creates a random broadcast channel"""
        uuid_hex = uuid.uuid4().hex
        id = '%s%s' % (prefix, uuid_hex)
        return cls(uri, id)

    def __init__(self, uri, id):
        self.uri = uri
        self.id = id

    def to_dict(self):
        return dict(uri=self.uri, id=self.id)

    def to_listening_dict(self):
        return dict(id=self.id)

class DeployOrder(object):
    @classmethod
    def from_dict(cls, d):
        app = d['app']
        commit = d.get('commit')
        return cls(app, commit)

    def __init__(self, app, commit=None):
        self.app = app
        self.commit = commit

    def to_dict(self):
        return dict(app=self.app, commit=self.commit)
