import fudge
from dploycenter.server import *

@fudge.test
def test_server_polling_router_route():
    import zmq

    fake_socket1 = fudge.Fake('socket1')
    fake_socket2 = fudge.Fake('socket2')
    fake_poller = fudge.Fake('Poller')
    
    fake_poller.expects('poll').returns({
        fake_socket1: zmq.POLLIN,
        fake_socket2: zmq.POLLIN,
    })

    fake_server = fudge.Fake()
    fake_server.expects('handle_socket1').with_args(fake_socket1)
    fake_server.expects('handle_socket2').with_args(fake_socket2)

    router = ServerPollingRouter(dict(socket1=fake_socket1, socket2=fake_socket2))
    # FIXME this is quick and simple but should we test like this?
    router._poller = fake_poller

    router.route(fake_server)
