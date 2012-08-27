import sys
import threading
import appcontainers
import copy
from dploylib import servers
from dploylib.services import Service


def start_cargo_builder(*args):
    """Runs the cargo builder"""
    builder = CargoBuilder.new(*args)
    builder.run()


class CargoBuilderThread(object):
    @classmethod
    def start_new(cls, settings, request):
        # Copy the request so there's no sharing issue between threads
        request_copy = copy.deepcopy(request)

        broadcast_in_uri = settings.get('broadcast_in_uri')
        completed_uri = settings.get('completed_uri')

        thread = threading.Thread(target=start_cargo_builder,
                args=(broadcast_in_uri, completed_uri, request_copy))
        cargo_builder_thread = cls(thread)
        cargo_builder_thread.start()

    def __init__(self, thread):
        self._thread = thread

    def start(self):
        self._thread.start()


class CargoBuilder(object):
    @classmethod
    def new(cls, broadcast_in_uri, completed_uri, request):
        return cls(broadcast_in_uri, completed_uri, request)

    def __init__(self, broadcast_in_uri, completed_uri, request):
        self._request = request
        self._completed_uri = completed_uri
        self._broadcast_in_uri = broadcast_in_uri

    def run(self):
        pass


class Release(object):
    @classmethod
    def deserialize(cls, raw_data):
        version = raw_data['version']
        app = raw_data['app']
        commit = raw_data['commit']
        env = raw_data['env']
        processes = raw_data['processes']
        return cls(version, app, commit, env, processes)

    def __init__(self, version, app, commit, env, processes):
        self.version = version
        self.app = app
        self.commit = commit
        self.env = env
        self.processes = processes

    def copy(self):
        Release(self.version, self.app)


class BuildRequest(object):
    @classmethod
    def deserialize(cls, raw_data):
        broadcast_id = raw_data['broadcast_id']
        app = raw_data['app']
        archive_uri = raw_data['archive_uri']
        update_message = raw_data['update_message']
        raw_release = raw_data['release']
        release = Release.deserialize(raw_release)
        return cls(broadcast_id, app, archive_uri, update_message, release)

    def __init__(self, broadcast_id, app, archive_uri, update_message,
            release):
        self.broadcast_id = broadcast_id
        self.app = app
        self.archive_uri = archive_uri
        self.update_message = update_message
        self.release = release


class EndpointRequest(object):
    @classmethod
    def deserialize(cls, raw_data):
        endpoint = raw_data['endpoint']
        data = raw_data['data']
        return cls(endpoint, data)

    def __init__(self, endpoint, data):
        self.endpoint = endpoint
        self.data = data

    def serialize(self):
        return dict(endpoint=self.endpoint, data=self.data)


class Response(object):
    def __init__(self, data):
        self.data = data

    def serialize(self):
        return dict(data=self.data)


class EndpointNotFound(Exception):
    pass


class RequestReactor(servers.Handler):
    def __call__(self, server, socket, received):
        request = received.obj
        endpoint = request.endpoint
        endpoint_handler = getattr(self, endpoint, None)
        if not endpoint_handler:
            raise EndpointNotFound()
        response_data = endpoint_handler(server, request)
        response_obj = Response(response_data)
        socket.send_obj(response_obj)


class BuildQueueReactor(RequestReactor):
    def __init__(self, *args, **kwargs):
        super(BuildQueueReactor, self).__init__(*args, **kwargs)
        self.queue = dict()

    def queue(self, server, request):
        """Enqueue some data"""
        build_request = BuildRequest.deserialize(request.data)
        return build_request

    def result(self, server, request):
        pass


class BuildQueueServer(servers.Server):
    def setup(self):
        self.active_job_envelopes = dict()
        self.app_container_service = appcontainers.setup_service()

    @servers.bind_in('request', 'router', obj=BuildRequest)
    def request_received(self, socket, received):
        envelope = received.envelope
        active_job_envelopes = self.active_job_envelopes
        job_id = envelope.id
        if job_id in active_job_envelopes:
            active_job_envelopes[job_id] = envelope
        request = envelope.obj
        CargoBuilderThread.start(request)

    @servers.bind_in('complete', 'pull')
    def job_completed(self, socket, received):
        import json
        data = received.data
        request_envelope = self.active_jobs[data]
        response_envelope = request_envelope.make_response('application/json',
                json.dumps({'status': 'completed'}))
        self.sockets.request.send_envelope(response_envelope)


class BroadcastServer(servers.Server):
    publish = servers.bind('out', 'pub')

    @servers.bind_in('in', 'pull')
    def broadcast_message(self, socket, received):
        envelope = received.envelope
        pub_socket = self.sockets.out
        pub_socket.send_envelope(envelope)


service = Service()
service.add_server('broadcast', BroadcastServer)
service.add_server('queue', BuildQueueServer)


def main():
    config_file = sys.argv[1]
    service.run(config_file=config_file)
