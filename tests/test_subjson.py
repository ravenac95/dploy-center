from nose.tools import *
from dploycenter import subjson

def test_encode():
    encoded = subjson.dumps('hello', dict(a=1))
    assert encoded == 'hello~~~{"a": 1}'

def test_decode():
    prefix, obj = subjson.loads('hello~~~{"a": 1, "b": 2}')
    assert prefix == 'hello'
    assert obj == dict(a=1,b=2)

@raises(ValueError)
def test_decode_no_json():
    subjson.loads('{"a": 1, "b": 2}')

def test_decode_multiple_separators():
    prefix, obj = subjson.loads('hello~~~{"a": 1, "b": "~~~"}')
    assert prefix == 'hello'
    assert obj == dict(a=1,b='~~~')
