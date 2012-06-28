import fudge
from dploycenter.foreman import *


class FakeApp(object):
    name = "name"
    md5 = "1234567890abcdef"


class TestBuildForeman(object):
    def setup(self):
        fake_builder = fudge.Fake('CargoBuilder')
        fake_app = fudge.Fake('Application')
        self.foreman = BuildForeman(fake_app, fake_builder)

        # Store fakes in class
        self.fake_builder = fake_builder
        self.fake_app = fake_app

    @fudge.test
    def test_prepare_cargo(self):
        fake_builder = self.fake_builder

        fake_builder.expects('prepare_container').with_args(self.fake_app)
        fake_builder.expects('build_app')
        fake_builder.expects('compress_container')

        self.foreman.prepare_cargo()

    @fudge.test
    def test_distribute_cargo(self):
        fake_builder = self.fake_builder

        fake_cargo = fudge.Fake('Cargo')

        fake_builder.expects('get_cargo').returns(fake_cargo)

        self.foreman.distribute_cargo()


class TestCargoBuilder(object):
    def setup(self):
        fake_cargo_service = fudge.Fake()
        self.fake_cargo_service = fake_cargo_service

        fake_app_container = fudge.Fake()
        self.fake_app_container = fake_app_container

        self.builder = CargoBuilder(fake_cargo_service)

    @fudge.test
    def test_prepare_container(self):
        builder = self.builder

        fake_app = FakeApp()

        (self.fake_cargo_service
                .expects('initialize_container').with_args(fake_app))

        builder.prepare_container(fake_app)

    @fudge.test
    def test_build_app(self):
        builder = self.builder
        builder._app_container = self.fake_app_container

        self.fake_app_container.expects('load_application')

        builder.build_app()
