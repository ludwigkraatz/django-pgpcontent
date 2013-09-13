import gnupg
import os, sys
from threading import local
from contextlib import contextmanager, GeneratorContextManager

from pgpcontent.settings import pgpcontent_settings

__all__ = [ 'gpg',
            'get_active_key', 'get_active_recipients', 'get_active_passphrase', 'pgp_active_encrypting_kwargs', 
            'pgp_activate_key',
            'import_pgp_keys'
            ]

_active = local()
_key_fingerprints = local()

try:
    gpg = gnupg.GPG(
        gnupghome   =   pgpcontent_settings.GNUPG_HOME,
        gpgbinary   =   pgpcontent_settings.GNUPG_BIN
    )
except BaseException, e:
    # set Environment var LC_ALL to en_US.UTF-8
    raise

if not gpg.encoding == 'UTF-8':
    gpg.encoding = 'UTF-8'
    
def _import_pgp_keys(keys):
    global _key_fingerprints
    import_result = gpg.import_keys(keys)
    _key_fingerprints.fingerprints = import_result.fingerprints
    #_key_fingerprints.value = gpg.list_keys() # just public keys

def import_pgp_keys(import_keys): 
    if callable(import_keys):
        import_keys = import_keys()
        if isinstance(import_keys, GeneratorContextManager):
            with import_keys as keys:
                _import_pgp_keys(keys)
        else:
            _import_pgp_keys(import_keys)
    else:
        _import_pgp_keys(import_keys)   


@contextmanager
def pgp_activate_key(fingerprint=None, passphrase=None, recipients=None, sign=False):
    global _active, _key_fingerprints
    
    if not hasattr(_key_fingerprints, 'fingerprints'):
        import_pgp_keys(pgpcontent_settings.IMPORT_KEYS)
    
    if fingerprint is not None and fingerprint not in _key_fingerprints.fingerprints:
        raise Exception, 'this fingerprint is unknown' # in this thread.. but doesn't matter
    
    if hasattr(_active, 'key_data'):
        fingerprint = _active.key_data.pop('fingerprint', fingerprint)
        passphrase  = _active.key_data.pop('passphrase', passphrase)
        recipients  = _active.key_data.pop('recipients', recipients)
        sign        = _active.key_data.pop('sign', sign)
    
    _active.key_data = {
        'fingerprint':  fingerprint or _key_fingerprints.fingerprints[0] if len(_key_fingerprints.fingerprints) else None,
        'passphrase':   passphrase,
        'recipients':   recipients or _key_fingerprints.fingerprints,
        'sign':         sign
    }
    
    try:
        yield
    finally:
        if hasattr(_active, "key_data"):
            del _active.key_data


def get_active_key():
    global _active
    if not hasattr(_active, 'key_data'):
        raise Exception, ''#TODO
    
    return _active.key_data.get('fingerprint')

def get_active_recipients():
    global _active
    if not hasattr(_active, 'key_data'):
        raise Exception, ''#TODO
    
    return _active.key_data.get('recipients')

def get_active_passphrase():
    global _active
    if hasattr(_active, "key_data"):
        try:
            return _active.key_data.pop('passphrase')
        except KeyError:
            raise Exception, 'accessing passphrase is just possible once!'
    raise Exception, ''#TODO

def pgp_active_encrypting_kwargs(passphrase=None):
    global _active
    if not hasattr(_active, 'key_data'):
        raise Exception, ''#TODO
    
    if _active.key_data.get('sign'):
        return {
                'sign':         get_active_key(),
                'passphrase':   passphrase or get_active_passphrase()
        }
    return {}

#input_data = gpg.gen_key_input(
#    name_email='testgpguser@mydomain.com',
#    passphrase='my passphrase')
#key = gpg.gen_key(input_data)
#print key
#imported = gpg.import_keys(key_data)
#from pprint import pprint
#pprint(imported.results)
#public_keys = gpg.list_keys()
#private_keys = gpg.list_keys(True)
#print 'public keys:'
#pprint(public_keys)
#print 'private keys:'
#pprint(private_keys)
#assert imported.count >= 1

#if "gnupg_keydata_public" and "gnupg_keydata_private" in os.environ:
#    key_data = os.environ["gnupg_keydata_public"]+"\n"+os.environ["gnupg_keydata_private"]
#else:
#    kex_data    =   open(settings.GNUPG_HOME+'expn.asc').read()


#from Crypto.PublicKey import RSA
#from Crypto import Random
#rng = Random.new().read
#RSAkey  = RSA.importKey('-----BEGIN RSA PRIVATE KEY-----\nMIIEowIBAAKCAQEAnvoACSBxVtutfU/TaI5Y4/8AnawTwrlXr/wU1+5e+yO1v/PR\nC8l8n1YiBAF4XdI8qrBImNZr/TNEiUzLkoyilcucKhr5Rp8vYxNWMz6XyuqM6v84\nUdr8ALeH4bWdbNj5wLvKdPOAa9Y3Q2L/hDCPj2jBbNl1jESUwjoihMrbf8S9U7Pb\nYTzvKJAYdaE2EqeyGYj+QMCl90zfXlHVWBS5lZ/BU/nFkS7hxqiO84ewUp0BUTAr\nMjTQ/3l9f9idFc/PoE78T9zTtHkFntZ6t2dUfOQjQSpptai/e9oCfgDXKoaIILJH\nHLWW1Yc/z/20A6wxyGWcWjafgz3soKkd5JgVUwIDAQABAoIBAQCJJu248gBWCxfV\nsHSXE5eku27wmHBD4lrAPR5OXBwdVmWKwPJs1NtrK4gVJJ+Pcb1dFNDM6tAnlX9f\nZJ2MRUBPM2X6/WJphxP+ycPoWevi6A/C/YS9OcuHYs8b7u9t5JMzr8+urhTw89Kh\nlFsU1EBGXP3ixokfBlvAZR86qThNNTZ6B0kDyTt1Uhivs8+dj6OB6h26P6L/7Edm\nFo/GSrc/XhweEp1/4bqeqSF79TDBf2l50kUu4ul+Nko6RV4xMyTdew7wwdhGPHKv\nKzgLCeqUP6b2wVcFz8MqNZyQCA/Rc7dInBv5xBe6nckWzGHX31MgPpJp/wADz/IU\nT1zV290hAoGBAMlVv9sHKHSTZ0KLeIRIzo/qJuIDByhIHHaDfIOYbLx5UGaPfIrx\nPoNOENao73Q0xPP1+sDb9pjPsP+50pVuAR+Ogq4fLifs/rTB0yQhACNGj7A+IBY0\nYi6RlEz/CGes1Lr+ItRgNrJ5N91EuNBeoPfvfPjFcHjkBBIiTxEzGeLVAoGBAMok\nCGFzFMpHJekfVLB6bzu29JOAOOWNppG9KJFHR1vy5uRpLcu4KC0P8rDu8MbRLdSz\nAyS/uLPz32r9ZBQfVZscuCn8qevWc89RCsRwZa6DT1hzPK9eQRw3cKfnvXwSQwM2\nk2lv1Mk8bYFGnxj7DEyO2Epvlel3XRtwTyQ7cRuHAoGALPQpf1Us0kKrVq9ffGHp\nRTbp8aLtcTAQsuGO5q8c8ERCEHRPQZK1+4lttxBHTvINW897ap5yhBIzmhW6kETc\nmVgvk4NAwgdno6J3a2S27ClwIdDtRyfxGCbHLx3umX98jDf8POEytUzdjVkvzs6i\nMFnX1I/5GfUHd6kTcGqxh/UCgYBbkztgunv+r4DTPehmEvF1ggsHD523ERcXCzTn\nq/z+AOrtK2Ed244H7COsWHMn/vfeVkLkUR7iF2dt1uGR5CgqHzanftmUCBFrKHHS\nUIEgMEiv73Tclby1hcA5sNi87qEBQaZCq/EgQYnyeQX2kTUfMc922Vp27CZ4Gccg\nyPUS3QKBgEuY5gKabwY8UM+hpnBLC7Vh9tWkTc3la6vRhLVmfyRZC8zv0qwwLhoI\nhzBgq4NWzSqRQ3130z/FEr53kUxiZxifIUZ9amxcPZ1Q4upq+wWUZtpBDi92Q/+W\niL0Ft4fntUZixkbCLt2qI49KzmU/zLSPPk/KoQYZhEjkL8G0u4H1\n-----END RSA PRIVATE KEY-----')
#public  = RSAkey.publickey()
#decrypt=RSAkey.decrypt
#encrypt=public.encrypt
#encrypt_arg =   None