from mock import patch
from dploycenter.queue import *


def test_deploy_order_from_dict():
    test_dict = dict(app='appname', archive_uri='uri', commit='commithash',
            update_message='msg', metadata_version=1)
    deploy_order = DeployRequest.from_dict(test_dict)

    assert deploy_order.commit == 'commithash'
    assert deploy_order.app == 'appname'
    assert deploy_order.archive_uri == 'uri'
    assert deploy_order.update_message == 'msg'
    assert deploy_order.metadata_version == 1


class TestDeployRequest(object):
    def setup(self):
        self.test_dict = dict(app='appname', archive_uri='uri',
                commit='commithash', update_message='msg', metadata_version=1)
        self.deploy_request = DeployRequest.from_dict(self.test_dict)

    def test_to_dict(self):
        assert self.deploy_request.to_dict() == self.test_dict


def test_broadcast_descriptor_to_dict():
    uri = 'uri'
    id = 'someid'
    channel = BroadcastDescriptor(uri, id)
    assert channel.to_dict() == dict(uri=uri, id=id)


@patch('uuid.uuid4')
def test_create_random_broadcast_descriptor(fake_uuid4):
    # WARNING does not actually create a random channel during test
    random_uuid = 'randomuuid'
    fake_uuid4.return_value.hex = random_uuid
    uri = 'uri'
    channel1 = BroadcastDescriptor.create_random(uri)
    assert channel1.id == random_uuid

    channel2 = BroadcastDescriptor.create_random(uri, prefix='test')
    assert channel2.id == 'test%s' % random_uuid
