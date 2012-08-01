"""
dploycenter.main
~~~~~~~~~~~~~~~~~~~~

Main entry point for this application
"""
import sys
import logging
import argparse
import ConfigParser
import zmq
import threading
import constants
import broadcast
import queue

logger = logging.getLogger('dploycenter')

parser = argparse.ArgumentParser(description='dploy-center server')
parser.add_argument('--daemon', action='store_true')
parser.add_argument('--quiet', action='store_true')
parser.add_argument('-c', '--config-file', dest='config_file',
        default='dploy.conf')


class ApplicationDying(Exception):
    pass


class ServerCoordinator(object):
    """Coordinates between server threads"""
    @classmethod
    def setup(cls, servers, options, config, control_socket=None):
        # Creates threads
        context = zmq.Context()
        control_socket = control_socket or constants.CONTROL_SOCKET_URI
        coordinator = cls(servers, options, config, context, control_socket)
        coordinator.setup_control_socket()
        return coordinator

    def __init__(self, servers, options, config, context, control_socket_uri,
            thread_poll_duration=0.5):
        self._servers = servers
        self._options = options
        self._config = config
        self._control_socket_uri = control_socket_uri
        self._threads = []
        self._context = context
        self._control_socket = None
        self._thread_poll_duration = thread_poll_duration

    def setup_control_socket(self):
        control_socket_uri = self._control_socket_uri
        logger.debug('Starting control socket @ "%s"' % control_socket_uri)
        control_socket = self._context.socket(zmq.PUB)
        control_socket.bind(control_socket_uri)
        self._control_socket = control_socket

    def start(self):
        threads = self._threads
        servers = self._servers
        logger.debug('Starting %d threads' % len(servers))
        for server in servers:
            thread = threading.Thread(target=server.start_server,
                    args=(self._context, self._control_socket_uri,
                        self._options, self._config))
            threads.append(thread)
            thread.start()

    def wait(self):
        """Wait for the threads"""
        threads = self._threads
        while True:
            some_dead = False
            for thread in threads:
                # Continually check the threads
                thread.join(self._thread_poll_duration)
                # If something is dead then the application has failed
                if not thread.is_alive():
                    some_dead = True
            # Kill the application if something has failed
            if some_dead:
                logger.debug('A thread has failed. Application is dying')
                raise ApplicationDying()

    def stop(self):
        control_socket = self._control_socket
        while True:
            # It will continually send the message to the threads
            # Until all threads are known to be done
            logger.debug('Sending shutdown message to threads')
            control_socket.send(constants.CONTROL_TOPIC)
            for thread in self._threads:
                thread.join(5)  # Wait for ten seconds
            if threading.active_count() == 1:
                logger.debug('Some threads still active. '
                        'Waiting for them to terminate')
                break


class DployCenterRunner(object):
    """Main Runner"""
    def __init__(self):
        pass

    def run(self, args=None):
        args = args or sys.argv[1:]
        options = parser.parse_args(args)
        raw_config = ConfigParser.ConfigParser()
        raw_config.read(options.config_file)
        # Turn config into a dictionary. For easy access
        config = dict(raw_config.items(constants.MAIN_CONFIG_SECTION))
        if not options.quiet:
            # Stdout handler
            handler = logging.StreamHandler()
            handler.setLevel(logging.DEBUG)
            logger.setLevel(logging.DEBUG)
            logger.addHandler(handler)
        coordinator = ServerCoordinator.setup(
                [broadcast, queue], options, config)
        logger.info('Starting DployCenter')
        coordinator.start()
        try:
            coordinator.wait()
        except (KeyboardInterrupt, ApplicationDying):
            pass
        finally:
            logger.info('Shutting down. Waiting for '
                    'child processes and threads')
            coordinator.stop()
            logger.info('Done.')


def main(args=None):
    runner = DployCenterRunner()
    runner.run(args=args)


if __name__ == '__main__':
    main()
