import testkit
from dploylib.transport import Socket
from dploycenter.main import *


def random_request():
    broadcast_id = testkit.random_string(10)
    app = testkit.random_string(10)
    archive_uri = 'some_archive_uri'
    update_message = 'This is an update message'
    commit = testkit.random_string(10)
    release = Release(1, app, commit, {}, {})
    request = BuildRequest(broadcast_id, app, archive_uri, update_message,
            release)
    return request


def make_a_request(request_uri, request):
    socket = Socket.connect_new('req', request_uri)
    socket.send_obj(request, id=request.broadcast_id)
    return socket.receive_envelope()


#if __name__ == '__main__':
#    main()
