import mock
from dploycenter.queue import *
    
def test_deploy_order_from_dict():
    test_dict = dict(app='appname', commit='commithash')
    deploy_order = DeployOrder.from_dict(test_dict)

    assert deploy_order.commit == 'commithash'
    assert deploy_order.app == 'appname'

def test_deploy_order_from_dict_no_commit():
    test_dict = dict(app='appname')
    deploy_order = DeployOrder.from_dict(test_dict)
    
    assert deploy_order.app == 'appname'

class TestDeployOrders(object):
    def setup(self):
        test_dict = dict(app='appname', commit='commithash')
        self.deploy_order = DeployOrder.from_dict(test_dict)

    def test_to_dict(self):
        test_dict = dict(app='appname', commit='commithash')
        assert self.deploy_order.to_dict() == test_dict

def test_broadcast_descriptor_to_dict():
    uri = 'uri'
    id = 'someid'
    channel = BroadcastDescriptor(uri, id)
    assert channel.to_dict() == dict(uri=uri, id=id)

@mock.patch('uuid.uuid4')
def test_create_random_broadcast_descriptor(fake_uuid4):
    # WARNING does not actually create a random channel during test
    random_uuid = 'randomuuid'
    fake_uuid4.return_value.hex = random_uuid
    uri = 'uri'
    channel1 = BroadcastDescriptor.create_random(uri)
    assert channel1.id == random_uuid
    
    channel2 = BroadcastDescriptor.create_random(uri, prefix='test')
    assert channel2.id == 'test%s' % random_uuid
