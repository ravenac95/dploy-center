import logging
import zmq
from . import constants
from .server import Server

logger = logging.getLogger('dploymentcenter.broadcast')

def start_server(context, control_socket_uri, options, config):
    server = ControlServer.create(context, control_socket_uri, options, 
            config)
    server.run()

class ControlServer(Server):
    def setup_sockets(self):
        control_socket_uri = self.config.get(constants.MAIN_CONFIG_SECTION, 
                'control-socket')
        
        notify_socket = self.context.socket(zmq.REP)
        notify_socket.bind(control_socket_uri)

        return {
            'notify': notify_socket
        }

    def handle_notify(self, socket):
        # FIXME it's just an echo server right now
        message = socket.recv()
        self.logger.info(message)
        socket.send(message)
