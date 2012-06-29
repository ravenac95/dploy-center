import fudge
from dploycenter.foreman import *


class FakeApp(fudge.Fake):
    def __init__(self, *args, **kwargs):
        super(FakeApp, self).__init__(*args, **kwargs)
        self.has_attr(name='name', commit='1234567890abcdef')

class TestBuildForeman(object):
    def setup(self):
        fake_builder = fudge.Fake('CargoBuilder')
        fake_app = fudge.Fake('Application')
        self.foreman = BuildForeman('fakepath', fake_app, fake_builder)

        # Store fakes in class
        self.fake_builder = fake_builder
        self.fake_app = fake_app

    @fudge.test
    def test_prepare_cargo(self):
        fake_builder = self.fake_builder

        fake_builder.expects('prepare').with_args(self.fake_app)
        fake_builder.expects('build_app')
        fake_builder.expects('create_cargo_file').with_args('fakepath')

        self.foreman.prepare_cargo()

class TestCargoBuilder(object):
    def setup(self):
        fake_app_container_service = fudge.Fake()
        self.fake_app_container_service = fake_app_container_service

        fake_app_container = fudge.Fake()
        self.fake_app_container = fake_app_container

        fake_cargo_file_writer = fudge.Fake('CargoFileWriter')
        self.fake_cargo_file_writer = fake_cargo_file_writer

        self.builder = CargoBuilder(fake_app_container_service, fake_cargo_file_writer)

    @fudge.patch('dploycenter.foreman.Cargo')
    def test_prepare_container(self, fake_cargo_cls):
        builder = self.builder

        fake_app = FakeApp()
        fake_container = fudge.Fake()

        (self.fake_app_container_service
                .expects('initialize_container').with_args(fake_app)
                .returns(fake_container))
        fake_cargo_cls.expects('from_app')

        builder.prepare(fake_app)

    @fudge.test
    def test_build_app(self):
        builder = self.builder
        builder._app_container = self.fake_app_container

        self.fake_app_container.expects('run_build')

        builder.build_app()

    @fudge.test
    def test_create_file(self):
        fake_app_container = self.fake_app_container
        fake_app_container.expects('compress').returns('compressed')
        
        builder = self.builder
        builder._app_container = fake_app_container
        fake_cargo = builder._cargo = fudge.Fake()

        (self.fake_cargo_file_writer.expects('from_compressed_app_container').
                with_args('fakepath', fake_cargo, 'compressed'))

        builder.create_cargo_file('fakepath')
