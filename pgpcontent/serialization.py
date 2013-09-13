"""
    celery.security.serialization
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Secure serializer.

"""
from __future__ import absolute_import

import base64

from kombu.serialization import registry, encode, decode
from kombu.utils.encoding import bytes_to_str, str_to_bytes, ensure_bytes

_default_serializer = 'json'

# TODO: pickle results in EOFError at some point when decoding the message (when de-pickling)

serializer_config = {
    'json':
        {
            'serializer_name': 'json',
            'encoding': 'utf-8',
            'content_type':'application/json'
        },
    'pickle':
        {
            'serializer_name': 'pickle',
            'encoding': 'binary',
            'content_type':'application/x-python-serialize'
        },
}


def b64encode(s):
    return bytes_to_str(base64.b64encode(str_to_bytes(s)))


def b64decode(s):
    return base64.b64decode(str_to_bytes(s))


class PGPSerializer(object):

    def __init__(self, serializer=None):
        self._serializer = serializer or serializer_config[_default_serializer]['serializer_name']

    def serialize(self, data):
        """serialize data structure into string"""
        content_type, content_encoding, body = encode(
            data, serializer=self._serializer)
        # What we sign is the serialized body, not the body itself.
        # this way the receiver doesn't have to decode the contents
        # to verify the signature (and thus avoiding potential flaws
        # in the decoding step).
        #body = ensure_bytes(body)
        return self._pack(body, content_encoding=content_encoding, content_type=content_type)

    def deserialize(self, data):
        """deserialize data structure from string"""
        payload = self._unpack(data)
        return decode(payload['body'], content_type=payload['content_type'],
                      content_encoding=payload['content_encoding'], force=True)

    def _pack(self, body, content_encoding, content_type, sep=str_to_bytes('\x00\x01')):
        from pgpcontent.settings import pgpcontent_settings
        from pgpcontent.encryption import pgp_encrypt, pgp_activate_key
        fields = sep.join(
            ensure_bytes(s) for s in [content_type,
                                      content_encoding, body]
        )
        with pgp_activate_key(pgpcontent_settings.DEFAULT_CELERY_KEY, recipients=pgpcontent_settings.DEFAULT_CELERY_RECIPIENTS):
            return pgp_encrypt(bytes_to_str(b64encode(ensure_bytes(fields))))

    def _unpack(self, payload, sep=str_to_bytes('\x00\x01')):
        from pgpcontent.settings import pgpcontent_settings
        from pgpcontent.encryption import pgp_decrypt, pgp_activate_key
        with pgp_activate_key(pgpcontent_settings.DEFAULT_CELERY_KEY):
            raw_payload = b64decode(ensure_bytes(pgp_decrypt(bytes_to_str(ensure_bytes(payload)))))

        v = raw_payload.split(sep)

        values = [bytes_to_str(v[0]), bytes_to_str(v[1]), bytes_to_str(v[2])]

        return {
            'content_type': values[0],
            'content_encoding': values[1],
            'body': values[2],
        }

def register_pgp(serializer=None):
    """register security serializer"""
    s = PGPSerializer(serializer=serializer)
    registry.register('pgpcontent_serializer', s.serialize, s.deserialize,
                      content_type="text/plain",
                      content_encoding="utf-8")