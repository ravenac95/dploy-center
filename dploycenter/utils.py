import zmq


class BroadcastOutputStream(object):
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

    def write(self, string):
        self._socket.send_multipart([self._id, string])

    def line(self, string):
        line = '%s\n' % string
        self.write(line)
