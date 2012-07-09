import zmq

class FakeGitosis(object):
    @classmethod
    def create(cls, notify_uri="tcp://127.0.0.1:5558", 
            broadcast_out_uri="tcp://127.0.0.1:5557"):
        client = cls()
        client.connect(notify_uri, broadcast_out_uri)
        return client

    def connect(self, notify_uri, broadcast_out_uri):
        context = zmq.Context()
        
        notify_socket = context.socket(zmq.REQ)
        notify_socket.connect(notify_uri)

        broadcast_out_socket = context.socket(zmq.SUB)
        # subscribe to all for now
        broadcast_out_socket.setsockopt(zmq.SUBSCRIBE, '')
        broadcast_out_socket.connect(broadcast_out_uri)

        self.broadcast_out_socket = broadcast_out_socket
        self.notify_socket = notify_socket
    
    def notify(self, message="hello"):
        notify_socket = self.notify_socket

        notify_socket.send(message)
        message = notify_socket.recv()
        
        print "Received: %s" % message

        broadcast_out_socket = self.broadcast_out_socket
        while True:
            msg = broadcast_out_socket.recv()
            if msg == 'END':
                break
            print msg
        print "done!"

def main():
    gitosis = FakeGitosis.create()
    gitosis.notify()

if __name__ == '__main__':
    main()
