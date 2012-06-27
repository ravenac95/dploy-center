class BuildForeman(object):
    """Coordinates packaging and distribution of cargo"""
    def __init__(self, application, builder):
        self.application = application
        self.builder = builder

    def prepare_cargo(self):
        builder = self.builder 
        
        builder.prepare_container(self.application)
        builder.build_application()
        builder.compress_container()

    def distribute_cargo(self):
        cargo = self.builder.get_cargo()
