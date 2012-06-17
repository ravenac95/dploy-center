"""
dploymentcenter.server
~~~~~~~~~~~~~~~~~~~~~~

A ZMQ-aware server class.
"""
import zmq
import logging
from . import constants

logger = logging.getLogger('dploymentcenter')

class ServerStopped(Exception):
    pass

class ServerPollingRouter(object):
    """Handles the routing of the zmq poller device"""
    @classmethod
    def from_dict(cls, listening_sockets):
        router = cls(listening_sockets)
        router.setup()
        return router

    def __init__(self, listening_sockets):
        self._listening_sockets = listening_sockets
        self._poller = None

    def setup(self):
        poller = zmq.Poller()
        for name, socket in self._listening_sockets.iteritems():
            poller.register(socket, zmq.POLLIN)
        self._poller = poller

    def route(self, server, timeout=None):
        sockets = dict(self._poller.poll(timeout=timeout))
        for socket_name, socket in self._listening_sockets.iteritems():
            if socket in sockets and sockets[socket] == zmq.POLLIN:
                method_name = 'handle_%s' % socket_name
                method = getattr(server, method_name, None)
                method(socket)
                if not method:
                    raise AttributeError('Method "%s" does not exist')

class Server(object):
    logger = logger

    @classmethod
    def create(cls, context, control_socket_uri, options, config):
        server = cls(context, control_socket_uri, options, config)
        server.setup()
        return server

    def __init__(self, context, control_socket_uri, options, config):
        self.context = context
        self.options = options
        self.config = config
        self._control_socket_uri = control_socket_uri
        self._control_socket = None
        self._listening_sockets = {}
    
    def connect_to_control_socket(self):
        """Subscribes to the control socket"""
        control_socket = self.context.socket(zmq.SUB)
        control_socket.setsockopt(zmq.SUBSCRIBE, constants.CONTROL_TOPIC)
        control_socket.connect(self._control_socket_uri)
        self._control_socket = control_socket
        self._listening_sockets['control'] = control_socket

    def setup(self):
        self.connect_to_control_socket()
        extra_listening_sockets = self.setup_sockets()
        self._listening_sockets.update(extra_listening_sockets)

    def setup_sockets(self):
        """Setup the server. Return the sockets to listen to as a dict"""
        return {}

    def run(self):
        # Create a router
        router = ServerPollingRouter.from_dict(self._listening_sockets)
        while True:
            # Route forever or until we are told to stop
            try:
                router.route(self)
            except ServerStopped:
                self.logger.debug('Server "%s" being stopped '
                        'intentionally' % self.__class__.__name__)
                break

    def handle_control(self, socket):
        control_string = socket.recv()
        if control_string == 'shutdown':
            self.logger.debug('Server "%s" received shutdown event '
                    'from control' % self.__class__.__name__)
            raise ServerStopped()
