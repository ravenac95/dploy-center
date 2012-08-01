"""
tests.test_broadcast
~~~~~~~~~~~~~~~~~~~~

Test the broadcast server
"""
from mock import Mock
from dploycenter.broadcast import BroadcastServer


def test_broadcast_server_handle_incoming_using_mock():
    # Basic Setup
    mock_context = Mock()
    mock_options = Mock()
    fake_config = {
        'broadcast-socket-in': 'uri',
        'broadcast-socket-out': 'uri',
    }
    mock_in_socket = Mock()
    mock_out_socket = Mock()

    server = BroadcastServer.create(mock_context, None,
            mock_options, fake_config)
    server.out_socket = mock_out_socket
    server.handle_incoming(mock_in_socket)

    mock_in_socket.recv_multipart.assert_called_with()
    mock_message = mock_in_socket.recv_multipart.return_value

    mock_out_socket.send_multipart.assert_called_with(mock_message)
