import zmq

class BuildForeman(object):
    """Coordinates creation of Cargo"""
    def __init__(self, cargo_file_path, app, builder):
        self.app = app
        self.builder = builder
        self.cargo_file_path = cargo_file_path

    def prepare_cargo(self):
        builder = self.builder

        builder.prepare(self.app)
        builder.build_app()
        builder.create_cargo_file(self.cargo_file_path)

class CargoBuilder(object):
    """Builds cargo"""
    def __init__(self, app_container_service, cargo_file_writer, 
            broadcast_channel):
        self.app_container_service = app_container_service
        self.cargo_file_writer = cargo_file_writer
        self.broadcast_channel = broadcast_channel

        self._cargo = None
        self._app_container = None

    def prepare(self, app):
        app_container = self.app_container_service.initialize_container(app)
        self._app_container = app_container
        cargo = Cargo.from_app(app)
        self._cargo = cargo

    def build_app(self):
        self.broadcast_channel.write('Running App Build')
        self._app_container.run_build(self.broadcast_channel)

    def create_cargo_file(self, file_path):
        compressed_file = self._app_container.compress()

        self.cargo_file_writer.from_compressed_app_container(file_path,
                self._cargo, compressed_file)

class Cargo(object):
    @classmethod
    def from_app(self, app):
        pass

class FakeAppContainer(object):
    def run_build(self, channel):
        print "running build"

    def compress(self):
        pass

class FakeAppContainerService(object):
    @classmethod
    def initialize_container(cls, *args, **kwargs):
        return FakeAppContainer()

class FakeCargoFileWriter(object):
    @classmethod
    def from_compressed_app_container(cls, *args, **kwargs):\
        pass

class BroadcastChannel(object):
    @classmethod
    def create(cls, context, channel_uri):
        channel = cls(context, channel_uri)
        channel.setup()
        return channel

    def __init__(self, context, channel_uri):
        self.context = context
        self.channel_uri = channel_uri
        self.channel_socket = None

    def setup(self):
        channel_socket = self.context.socket(zmq.PUSH)
        channel_socket.connect(self.channel_uri)
        self.channel_socket = channel_socket

    def write(self, message):
        self.channel_socket.send(message)

class CargoCatalog(object):
    @classmethod
    def new_path(cls, app):
        return '/tmp/%(name)s.%(commit)s.cargo' % app

class CargoBuildService(object):
    def __init__(self, context, broadcast_channel):
        self.context = context
        self.broadcast_channel = broadcast_channel

    def build_cargo_for_app(self, app):
        # Try to get the cargo. Just in case it already exists
        broadcast_channel = self.broadcast_channel
        broadcast_channel.write('Building cargo for %s' % app['name'])

        cargo_path = CargoCatalog.new_path(app)
        builder = CargoBuilder(FakeAppContainerService, FakeCargoFileWriter,
                broadcast_channel)

        foreman = BuildForeman(cargo_path, app, builder)

        foreman.prepare_cargo()
        

        broadcast_channel.write('END')
        return cargo_path

        
def start_cargo_build_service(app, broadcast_in_uri):
    """Initializes the cargo build service"""
    context = zmq.Context()
    broadcast_channel = BroadcastChannel.create(context, broadcast_in_uri)

    service = CargoBuildService(context, broadcast_channel)
    service.build_cargo_for_app(app)
