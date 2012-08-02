import logging
import zmq
import threading
import uuid
from .server import Server
from .utils import BroadcastStream

logger = logging.getLogger('dploycenter')


def start_server(context, control_socket_uri, options, config):
    server = DeployQueueServer.create(context, control_socket_uri, options,
            config)
    server.run()


class DeployDirector(object):
    def __init__(self, app_service_client,
            cargo_build_service_client,
            deploy_request,
            broadcast_descriptor):
        self._app_service_client = app_service_client
        self._cargo_build_service_client = cargo_build_service_client
        self._deploy_request = deploy_request
        self._broadcast_descriptor = broadcast_descriptor

    def complete_deployment(self):
        deploy_request = self._deploy_request
        app_name = deploy_request.app

        broadcast = BroadcastStream.bind_to_descriptor(
                self._broadcast_descriptor)
        logger.debug('Processing DeployRequest for "%s"' % app_name)

        app_service_client = self._app_service_client
        # Get the current app's metadata from app service
        # This should probably lock the app for any building so multiple jobs
        # don't go at once.
        broadcast.line('Retrieving App metadata for "%s"' % app_name)
        app_metadata = app_service_client.open_metadata_for_build(
                version=self._deploy_request.metadata_version)
        # Create a build request
        build_request = AppBuildRequest.create(deploy_request,
                app_metadata, self._broadcast_descriptor)
        # Send the build request
        broadcast.line('Initializing cargo build for "%s"' % app_name)
        new_metadata = self._cargo_build_service_client.send_build_request(
                build_request)
        # Update the app's metadata
        app_service_client.close_metadata(new_metadata)
        broadcast.line('Stopping any active deployments for "%s"' % app_name)
        broadcast.line('Deploying cargo to 2 zones')
        broadcast.line('Deployment completed')
        broadcast.completed()

        logger.debug('End Processing DeployRequest for "%s"' % app_name)


def handle_deploy_request(config, deploy_request, broadcast_descriptor):
    """Spawns the DeployDirector"""
    app_service_client = AppServiceClient(config['app-service-socket'])
    cargo_build_service_client = CargoBuildServiceClient(
            config['cargo-build-service-socket'])
    director = DeployDirector(app_service_client, cargo_build_service_client,
            deploy_request, broadcast_descriptor)
    director.complete_deployment()


class DeployQueueServer(Server):
    """Queues DeployRequests

    DeployRequests can be made through one of the following actions:

        1. A user pushes a git repository
        2. A user changes the environment settings
        3. A user changes the required services
        4. The system forces an upgrade of the Cargo's AppContainer Base
    """
    def __init__(self, *args, **kwargs):
        super(DeployQueueServer, self).__init__(*args, **kwargs)
        self.queue = []

    def setup(self):
        self._broadcast_in_uri = self.config['broadcast-socket-in']

    def setup_sockets(self):
        queue_socket_uri = self.config['queue-socket']

        queue_socket = self.context.socket(zmq.REP)
        queue_socket.bind(queue_socket_uri)

        return {
            'queue': queue_socket,
        }

    def handle_queue(self, socket):
        # Receive the raw DeployRequest data
        raw_deploy_request = socket.recv_json()

        # Create a DeployRequest out of the raw data
        deploy_request = DeployRequest.from_dict(raw_deploy_request)

        # Create a BroadcastDescriptor
        broadcast_descriptor = BroadcastDescriptor.from_request(
                self._broadcast_in_uri, deploy_request)

        # Send the listening channel back to the caller
        socket.send_json({'ready': True})

        # Start the worker thread
        config_copy = self.config.copy()
        thread_args = [config_copy, deploy_request,
                broadcast_descriptor]
        thread = threading.Thread(target=handle_deploy_request,
                args=thread_args)
        thread.start()


class BroadcastDescriptor(object):
    @classmethod
    def create_random(cls, uri, prefix=''):
        """Creates a random broadcast channel"""
        uuid_hex = uuid.uuid4().hex
        id = '%s%s' % (prefix, uuid_hex)
        return cls(uri, id)

    @classmethod
    def from_request(cls, uri, deploy_request):
        return cls(uri, deploy_request.broadcast_id)

    def __init__(self, uri, id):
        self.uri = uri
        self.id = id

    def to_dict(self):
        return dict(uri=self.uri, id=self.id)

    def to_listening_dict(self):
        return dict(id=self.id)


class DeployRequest(object):
    @classmethod
    def from_dict(cls, data):
        app = str(data['app'])
        archive_uri = data['archive_uri']
        commit = str(data['commit'])
        update_message = data['update_message']
        metadata_version = int(data['metadata_version'])
        broadcast_id = str(data['broadcast_id'])
        return cls(broadcast_id, app,
                archive_uri, commit, update_message, metadata_version)

    def __init__(self, broadcast_id, app, archive_uri, commit, update_message,
            metadata_version):
        self.broadcast_id = broadcast_id
        self.app = app
        self.archive_uri = archive_uri
        self.commit = commit
        self.update_message = update_message
        self.metadata_version = metadata_version

    def to_dict(self):
        return dict(broadcast_id=self.broadcast_id,
                app=self.app,
                archive_uri=self.archive_uri,
                commit=self.commit,
                update_message=self.update_message,
                metadata_version=self.metadata_version,
                )


class AppServiceClient(object):
    def __init__(self, *args, **kwargs):
        pass

    def open_metadata_for_build(self, *args, **kwargs):
        pass

    def close_metadata(self, *args, **kwargs):
        pass


class AppBuildRequest(object):
    @classmethod
    def create(cls, *args):
        return cls()


class CargoBuildServiceClient(object):
    def __init__(self, *args, **kwargs):
        pass

    def send_build_request(self, *args, **kwargs):
        pass
