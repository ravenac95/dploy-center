"""
tests/large/fake_client.py
~~~~~~~~~~~~~~~~~~~~~~~~~~

A fake client for the dploy-center.
"""
import zmq
import json
from fixtures import CLIENT_FIXTURES


def dploy_center_test_client(fixture_key, request_uri, listen_uri):
    # Setup Fixture
    request_fixtures = CLIENT_FIXTURES
    common_messages = request_fixtures['__common__']
    fixture, expected_messages = request_fixtures[fixture_key]

    broadcast_id = fixture['broadcast_id']

    # Setup context
    context = zmq.Context()

    # Setup request socket
    request_socket = context.socket(zmq.REQ)
    request_socket.connect(request_uri)

    # Setup listen socket
    listen_socket = context.socket(zmq.SUB)
    listen_socket.connect(listen_uri)

    # Connect the listening socket.
    listen_socket.setsockopt(zmq.SUBSCRIBE, broadcast_id)

    # Send a request
    request_socket.send_json(fixture)

    # Wait for response
    response = request_socket.recv_json()

    # Check that the response is ready
    assert response['ready'] == True, "Server is not ready"

    # Start listening to broadcast
    print 'Beginning listening loop'
    broadcast_messages = []
    while True:
        raw_message = listen_socket.recv_multipart()
        received_id = str(raw_message[0])
        id_match_error_msg = "Unexpected broadcast ID received %s != %s" % (
                received_id, broadcast_id)
        assert received_id == broadcast_id, id_match_error_msg

        broadcast_message = json.loads(raw_message[1])
        broadcast_messages.append(broadcast_message)

        print "Receiving message: %s" % broadcast_message
        if broadcast_message['message']['type'] == 'completed':
            break
    verify(broadcast_messages, expected_messages, common_messages)


def verify(messages, expected_output, common_messages):
    all_messages = []
    all_messages.extend(expected_output)
    all_messages.extend(common_messages)

    for message in messages:
        error_message = 'Received unexpected message "%s"' % message
        assert message in all_messages, error_message
