from django.utils.encoding import smart_unicode

from pgpcontent.keys import gpg, get_active_key, get_active_recipients, get_active_passphrase, pgp_activate_key, pgp_active_encrypting_kwargs

__all__ = ['activate_key', 'pgp_decrypt', 'pgp_encrypt', 'pgp_recrypt']

def pgp_decrypt(data, passphrase=None):
    """ wrapper for pgp.decrypt method """
    if data == None:
        raise EncryptionError, "data is none"
    
    decrypted_data   =   gpg.decrypt(data, passphrase=passphrase or get_active_passphrase())
    if decrypted_data.ok:
        try:
            return decrypted_data.data.decode('utf-8')
        except UnicodeDecodeError:
            return decrypted_data.data#.decode('ascii')
        
    else:
        raise Exception, ("Key missing?" , decrypted_data.status, decrypted_data.stderr)#EncryptionError


def pgp_encrypt(data, passphrase=None):
    """ wrapper for pgp.encrypt method """
    if data == None:
        raise DecryptionError, "data is none"
    
    encrypted_data  =   gpg.encrypt(data, get_active_recipients(), **pgp_active_encrypting_kwargs(passphrase))
    if encrypted_data.ok:
        return smart_unicode(encrypted_data) # TODO: not take smart_unicode?
    else:
        raise Exception, ("couldnt encrypt?" ,encrypted_data.status, encrypted_data.stderr)#DecryptionError

def pgp_recrypt(data, passphrase=None):
    """ decrypts message and then encrypts it again for new recipients """
    passphrase = passphrase or get_active_passphrase()
    
    return pgp_encrypt(pgp_decrypt(data, passphrase=passphrase), passphrase=passphrase)
