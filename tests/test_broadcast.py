"""
tests.test_broadcast
~~~~~~~~~~~~~~~~~~~~

Test the broadcast server
"""
import fudge
from dploycenter.broadcast import BroadcastServer

@fudge.test
def test_broadcast_server_handle_incoming():
    # Basic Setup
    fake_context = fudge.Fake()
    fake_context.is_a_stub()

    fake_options = fudge.Fake()
    fake_options.is_a_stub()
    
    fake_config = fudge.Fake()
    fake_config.is_a_stub()
    
    # Test expectations
    fake_in_socket = fudge.Fake()
    # Fake the receiving
    fake_message = fake_in_socket.expects('recv_multipart').returns_fake()
    
    fake_out_socket = fudge.Fake()
    fake_out_socket.expects('send_multipart').with_args(fake_message)

    server = BroadcastServer.create(fake_context, None,
            fake_options, fake_config)

    server.out_socket = fake_out_socket
    server.handle_incoming(fake_in_socket)
