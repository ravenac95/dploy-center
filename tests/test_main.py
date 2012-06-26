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
    fake_config = fudge.Fake('config')

    fake_thread = fake_thread_cls.expects_call().returns_fake()
    fake_thread.expects('start')
    fake_thread.expects('join')

    fake_active.expects_call().returns(1)

    coordinator = ServerCoordinator.setup(fake_servers, fake_options, fake_config)
    coordinator.start()
    coordinator.stop()
