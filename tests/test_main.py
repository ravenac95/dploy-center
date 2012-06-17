import fudge
from testkit import ContextUser
from dploymentcenter.main import *
from .utils import verify, reset

@fudge.patch('threading.Thread', 'threading.active_count')
def test_coordinator_start_and_stop(fake_thread_cls, fake_active):
    # Fake Servers
    fake_server1 = fudge.Fake('server1')
    fake_server2 = fudge.Fake('server2')
    fake_servers = [fake_server1, fake_server2]
    fake_server1.provides('start_server')
    fake_server2.provides('start_server')
    # Fake Options
    fake_options = fudge.Fake('options')

    fake_thread = fake_thread_cls.expects_call().returns_fake()
    fake_thread.expects('start')
    fake_thread.expects('join')

    fake_active.expects_call().returns(1)

    coordinator = ServerCoordinator.setup(fake_servers, fake_options)
    coordinator.start()
    coordinator.stop()

class TestServerCoordinator(object):
    def setup(self):
        # Fake Servers
        fake_server1 = fudge.Fake('server1')
        fake_server2 = fudge.Fake('server2')
        fake_servers = [fake_server1, fake_server2]
        fake_server1.provides('start_server')
        fake_server2.provides('start_server')
        # Fake Options
        fake_options = fudge.Fake('options')

        # Patch threading
        patch_context = fudge.patch('threading.Thread', 'zmq.Context')
        self.context = ContextUser(patch_context)
        fake_thread_cls, fake_zmq_context = self.context.enter()
        
        # Fake threading.Thread Setup
        fake_thread = fake_thread_cls.is_callable().returns_fake()
        fake_thread.expects('start')

        # Fake zmq.Context Setup
        fake_socket = fake_zmq_context.is_callable().returns_fake()
        fake_socket.is_a_stub()

        self.fake_thread_cls = fake_thread_cls
        self.fake_thread = fake_thread
        self.fake_server1 = fake_server1
        self.fake_server2 = fake_server2
        self.fake_zmq_context = fake_zmq_context
        self.coordinator = ServerCoordinator.setup(fake_servers, fake_options)

    def teardown(self):
        reset()
        self.context.exit()

