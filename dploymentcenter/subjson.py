"""
builddaemon.subjson
~~~~~~~~~~~~~~~~~~~

ZMQ subscribe compatible json.

In order to accomplish this the json string is encoded like so::
    
    [alpha_numeric_prefix]~~~[json_string]

"""
import json
import re

PREFIX_SEPARATOR = '~~~'

def dumps(prefix, obj, *json_args, **json_kwargs):
    obj_string = json.dumps(obj, *json_args, **json_kwargs)
    return '%s%s%s' % (prefix, PREFIX_SEPARATOR, obj_string)

def loads(string, *json_args, **json_kwargs):
    split_string = string.split(PREFIX_SEPARATOR)
    if len(split_string) < 2:
        raise ValueError('No SubJSON string found')
    prefix = split_string[0]
    json_string = PREFIX_SEPARATOR.join(split_string[1:])
    obj = json.loads(json_string, *json_args, **json_kwargs)
    return prefix, obj
