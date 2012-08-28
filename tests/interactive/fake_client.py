import testkit
from dploylib.transport import Socket
from dploycenter.main import *


def random_request():
    broadcast_id = testkit.random_string(10)
    app = testkit.random_string(10)
    archive_uri = 's3://dploy-bwa-repos/testing/testing-6c2bff0080aa6a9da3698e7346937597dcea4496.tar.gz'
    update_message = 'This is an update message'
    commit = testkit.random_string(10)
    release = Release(1, app, commit, {}, {})
    request = BuildRequest(broadcast_id, app, archive_uri, update_message,
            release)
    return request


def send_a_request(request_uri, request):
    socket = Socket.connect_new('req', request_uri)
    socket.send_obj(request, id=request.broadcast_id)
    return socket.receive_envelope()


def send_random_request(request_uri):
    request = random_request()
    send_a_request(request_uri, request)


#if __name__ == '__main__':
#    main()
