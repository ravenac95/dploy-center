import logging
import zmq
import multiprocessing
from . import constants
from .server import Server
from .foreman import start_cargo_build_service


logger = logging.getLogger('dploycenter.broadcast')

def start_server(context, control_socket_uri, options, config):
    server = ControlServer.create(context, control_socket_uri, options, 
            config)
    server.run()

class ControlServer(Server):
    def setup_sockets(self):
        notify_socket_uri = self.config.get(constants.MAIN_CONFIG_SECTION, 
                'notify-socket')
        
        notify_socket = self.context.socket(zmq.REP)
        notify_socket.bind(notify_socket_uri)

        return {
            'notify': notify_socket
        }

    def handle_notify(self, socket):
        message = socket.recv()
        self.logger.info(message)
        socket.send(message)

        broadcast_in_uri = self.config.get(constants.MAIN_CONFIG_SECTION,
                'broadcast-socket-in')

        app = dict(commit="1234", name="mytestapp")

        # Start the worker process
        process = multiprocessing.Process(target=start_cargo_build_service, 
                args=[app, broadcast_in_uri])
        process.start()
