import sys
import threading
import appcontainers
import copy
import logging
from dploylib import servers
from dploylib.services import Service
from dploylib.transport import Context


logger = logging.getLogger('dploycenter.main')


def start_cargo_builder(*args):
    """Runs the cargo builder"""
    print "Starting cargo builder"
    builder = CargoBuilder.new(*args)
    builder.run()


class CargoBuilderThread(object):
    @classmethod
    def start_new(cls, job_id, settings, request, app_container):
        # Copy the request so there's no sharing issue between threads
        request_copy = copy.deepcopy(request)

        broadcast_in_uri = settings.get('broadcast_in_uri')
        completed_uri = settings.get('completed_uri')

        thread = threading.Thread(target=start_cargo_builder,
                args=(job_id, broadcast_in_uri, completed_uri, request_copy,
                    app_container))
        cargo_builder_thread = cls(thread)
        cargo_builder_thread.start()
        return cargo_builder_thread

    def __init__(self, thread):
        self._thread = thread

    def start(self):
        self._thread.start()


class CargoBuilder(object):
    @classmethod
    def new(cls, job_id, broadcast_in_uri, completed_uri, request,
            app_container):
        return cls(job_id, broadcast_in_uri, completed_uri, request,
                app_container)

    def __init__(self, job_id, broadcast_in_uri, completed_uri, request,
            app_container):
        self._request = request
        self._completed_uri = completed_uri
        self._broadcast_in_uri = broadcast_in_uri
        self._app_container = app_container
        self._job_id = job_id

    def run(self):
        logger.debug('Starting thread')
        context = Context.new()
        app_container = self._app_container
        app_container.start()
        app_container.stop()
        #app_container.make_image(path_to_cargo)

        print "Done with %s" % self._job_id

        completed_socket = context.socket('push')
        completed_socket.connect(self._completed_uri)
        completed_socket.send_obj(self._request.release, id=self._job_id)


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

    def serialize(self):
        return dict(version=self.version, app=self.app, commit=self.commit,
                env=self.env, processes=self.processes)


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

    def serialize(self):
        return dict(broadcast_id=self.broadcast_id,
                app=self.app, archive_uri=self.archive_uri,
                update_message=self.update_message,
                release=self.release.serialize())


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
        self._active_job_envelopes = dict()
        self._app_container_service = appcontainers.setup_service()

    @servers.bind_in('request', 'router', obj=BuildRequest)
    def request_received(self, socket, received):
        envelope = received.envelope
        active_job_envelopes = self._active_job_envelopes
        job_id = envelope.id
        print "making job %s" % job_id
        if job_id in active_job_envelopes:
            # Raise some kind error
            raise Exception()
        request = received.obj
        print "RECEIVED"
        print request

        # Start a new container
        app_container = self._app_container_service.provision()
        unmanaged_app_container = app_container.unmanaged_container
        active_job_envelopes[job_id] = (envelope, app_container)
        CargoBuilderThread.start_new(job_id, self.settings, request,
                unmanaged_app_container)

    @servers.bind_in('complete', 'pull')
    def job_completed(self, socket, received):
        import json
        active_job_envelopes = self._active_job_envelopes
        data = received.envelope.data
        job_id = received.envelope.id
        request_envelope, app_container = active_job_envelopes[job_id]

        # Clean up work on the app container
        app_container.destroy()

        # Send the request back to the requester
        response_envelope = request_envelope.response_envelope(
                'application/json',
                json.dumps({'status': 'completed'}))
        print data
        self.sockets.request.send_envelope(response_envelope)
        del active_job_envelopes[job_id]


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

if __name__ == '__main__':
    main()
