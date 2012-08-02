import zmq
import json


class BroadcastStream(object):
    @classmethod
    def bind_to_descriptor(cls, descriptor, context=None, socket_type=None):
        context = context or zmq.Context()
        socket_type = socket_type or zmq.PUSH
        broadcast_socket = context.socket(socket_type)
        broadcast_socket.connect(descriptor.uri)
        return cls(broadcast_socket, descriptor.id)

    def __init__(self, socket, id):
        self._socket = socket
        self._id = id

    def _send_message(self, message_type, sub_type, data=None):
        message_dict = dict(
            type=message_type,
            message=dict(
                type=sub_type,
                data=data,
            ),
        )
        message_json = json.dumps(message_dict)
        self._socket.send_multipart([self._id, message_json])

    def line(self, string):
        self._send_message('output', 'line', string)

    def write(self, string):
        self._send_message('output', 'raw', string)

    def completed(self):
        self._send_message('status', 'completed')

    def error(self, error_message):
        self._send_message('status', 'error', error_message)
