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
    def __init__(self, app_container_service, cargo_file_writer):
        self.app_container_service = app_container_service
        self.cargo_file_writer = cargo_file_writer

        self._cargo = None
        self._app_container = None

    def prepare(self, app):
        app_container = self.app_container_service.initialize_container(app)
        self._app_container = app_container
        cargo = Cargo.from_app(app)
        self._cargo = cargo

    def build_app(self):
        self._app_container.run_build()

    def create_cargo_file(self, file_path):
        compressed_file = self._app_container.compress()

        self.cargo_file_writer.from_compressed_app_container(file_path,
                self._cargo, compressed_file)

class Cargo(object):
    @classmethod
    def from_app(self, app):
        pass
