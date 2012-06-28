class BuildForeman(object):
    """Coordinates packaging and distribution of cargo"""
    def __init__(self, application, builder):
        self.application = application
        self.builder = builder

    def prepare_cargo(self):
        builder = self.builder

        builder.prepare_container(self.application)
        builder.build_app()
        builder.compress_container()

    def distribute_cargo(self):
        self.builder.get_cargo()


class CargoBuilder(object):
    """Builds cargo"""
    def __init__(self, cargo_service):
        self.cargo_service = cargo_service

    def prepare_container(self, application):
        self.cargo_service.initialize_container(application)

    def build_app(self):
        pass
