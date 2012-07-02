import logging
import zmq
from . import constants
from .server import Server

logger = logging.getLogger('dploycenter.broadcast')

def start_server(context, control_socket_uri, options, config):
    server = BroadcastServer.create(context, control_socket_uri, options, 
            config)
    server.run()

class BroadcastServer(Server):
    def setup_sockets(self):
        broadcast_in_uri = self.config.get(constants.MAIN_CONFIG_SECTION, 
                'broadcast-socket-in')
        broadcast_out_uri = self.config.get(constants.MAIN_CONFIG_SECTION, 
                'broadcast-socket-out')
        
        in_socket = self.context.socket(zmq.PULL)
        in_socket.bind(broadcast_in_uri)

        out_socket = self.context.socket(zmq.PUB)
        out_socket.bind(broadcast_out_uri)

        self.out_socket = out_socket
        return {
            'incoming': in_socket,
        }

    def handle_incoming(self, socket):
        """Simple routes the incoming message to the PUB socket"""
        message = socket.recv_multipart()
        self.out_socket.send_multipart(message)
