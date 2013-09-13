from django.db.models import fields
from django.utils.encoding import smart_unicode

from pgpcontent.encryption import pgp_encrypt, pgp_decrypt
from pgpcontent import mixins

class PGPTextField(fields.TextField):
    """
    A PGP TextField is used to encrypt the value of this field via PGP encryption.
    
    1. Accessing ``instance.[PGPField.attr_name]`` results in the pgp encrypted message.
        this is necessary to prevent sensitive data being represented unencrypted in
        exceptions / logs / in public caused by wrong usage
    2. in Order to access the decrypted value, use the ``get_decrypted_content`` method
    """
    
    def __init__(self, *args, **kwargs):
        if kwargs.get('unique', False):
            # pgp messages are non-persistent. changing one receiver will cause a totally
            # new message. thatswhy you should never use them as foreign keys
            raise Exception, 'PGP Field should never be used for ForeignKey target!'
        super(PGPTextField, self).__init__(*args, **kwargs)    
    
    def _is_data_encrypted(self, data):
        """
        @brief is raw_data encrypted
        """
        if data == None:
            return False
        return data[:27] == "-----BEGIN PGP MESSAGE-----"
    
    def _get_decrypted(self, value):
        if self._is_data_encrypted(value):
            return pgp_decrypt(value)
        
        return value
    
    def _get_encrypted(self, value):
        if value is None:
            return value
        
        if self._is_data_encrypted(value):
            return value
        
        return pgp_encrypt(value)    
        
    def conditional_encrypt_value(self, value, obj_or_class=None):
        """ any subclass should decide when a value should be encrypted or not """
        return self._get_encrypted(value, obj_or_class)    

    def db_type(self, connection=None):
        """
        Return the special uuid data type on Postgres databases.
        """
        return 'text'

    def get_db_prep_value(self, value, connection, prepared=False):
        """
        Casts uuid.UUID values into the format expected by the back end
        """
        return self.conditional_encrypt_value(value)

    #def value_to_string(self, obj):
    #    val = self._get_val_from_obj(obj)
    #    if val is None:
    #        data = ''
    #    else:
    #        data = unicode(val)
    #    return data

    def to_python(self, value):
        """
        Returns the PGP encrypted text returned by the database.
        """
        if not value:
            return None
        return smart_unicode(value) #TODO: just return value?

    #def formfield(self, **kwargs):
    #    defaults = {
    #        'form_class': forms.TextField,
    #        'widget':      Textarea,
    #        ##'max_length': self.max_length,
    #    }
    #    defaults.update(kwargs)
    #    return super(UUIDField, self).formfield(**defaults)
    
class AutoPGPTextField(PGPTextField):
    """
    An AutoPGP TextField basically is a PGP Field that stores content in reference to some Model.
    . See ForceEncryptionMixin
    """
    
    def conditional_encrypt_value(self, value, obj_or_class=None):
        if obj_or_class is None:
            return value #not for an object
            # TODO exception
            raise Exception, '"%s" requires an object as reference when setting the content' % self.__class__.__name__
        
        if type(obj_or_class) == type:
            if not issubclass(obj_or_class, mixins.ForceEncryptionMixin):
                return value
        elif not isinstance(obj_or_class, mixins.ForceEncryptionMixin):
            return value
        
        return self._get_encrypted(value)   