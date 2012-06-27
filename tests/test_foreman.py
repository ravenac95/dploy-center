import fudge
from dploycenter.foreman import *

class TestBuildForeman(object):
    def setup(self):
        fake_builder = fudge.Fake('CargoBuilder')
        fake_application = fudge.Fake('Application')
        foreman = BuildForeman(fake_application, fake_builder)
    
        # Store fakes in class
        self.fake_builder = fake_builder
        self.fake_application = fake_application

        # Store foreman in class
        self.foreman = foreman
    
    @fudge.test
    def test_prepare_cargo(self):
        fake_builder = self.fake_builder

        fake_builder.expects('prepare_container').with_args(self.fake_application)
        fake_builder.expects('build_application')
        fake_builder.expects('compress_container')

        self.foreman.prepare_cargo()

    @fudge.test
    def test_distribute_cargo(self):
        fake_builder = self.fake_builder

        fake_cargo = fudge.Fake('Cargo')

        fake_builder.expects('get_cargo').returns(fake_cargo)

        self.foreman.distribute_cargo()


