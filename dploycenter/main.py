import sys
from dploylib import servers
from dploylib.services import Service


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


class ResponseServer(servers.Server):
    @servers.bind_in('request', 'rep', obj=BuildRequest)
    def request_received(self, socket, received):
        broadcast_in_uri = self._settings['broadcast_in_uri']
        build_request = received.obj
        print build_request
        print broadcast_in_uri


class BroadcastServer(servers.Server):
    publish = servers.bind('out', 'pub')

    @servers.bind_in('in', 'pull')
    def broadcast_message(self, socket, received):
        envelope = received.envelope
        pub_socket = self.sockets.out
        pub_socket.send_envelope(envelope)


service = Service()
service.add_server('broadcast', BroadcastServer)
service.add_server('queue', ResponseServer)


def main():
    config_file = sys.argv[1]
    service.run(config_file=config_file)
