from django.template import Template, Context
from django.utils.encoding import force_text
from django.utils.html import mark_safe
from django.db.models import Model, fields

from pgpcontent.fields import AutoPGPTextField
from pgpcontent.settings import pgpcontent_settings

class abstractPGPContent(Model):
    class Meta:
        abstract = True    
    
    # default: content = PGPTextField(null=True, blank=True)
    pgpcontent_settings.OBJECT_CONTENT_MODEL__CONTENT_ATTR_NAME     =   pgpcontent_settings.OBJECT_CONTENT_FIELD(null=True, blank=True)
    
    def __init__(self, *args, **kwargs):
        self._pgp__object_or_class = None
        super(abstractPGPContent, self).__init__(*args, **kwargs)
    
    def __setattr__(self, attr_name, value):
        # if we're setting the content
        if attr_name == pgpcontent_settings.OBJECT_CONTENT_MODEL__CONTENT_ATTR_NAME:            
            value = self.prepare_content(value)
        
        return super(abstractPGPContent, self).__setattr__(attr_name, value)
    
    def get_content(self, *args, **kwargs):
        return self.content
    
    def get_content_field(self, ):        
        meta    =   self.__class__._meta
        pgp_field = None
        
        for field in meta.local_fields: # TODO: just meta.fields?
            if attr_name == field.attname:
                pgp_field = field
                break
            
        return pgp_field    
    
    def get_encrypted_content(self, ):
        _get_decrypted
        
    def set_content(self, valuee, object_or_class=None):
        self._pgp__object_or_class = object_or_class
        return setattr(self, 'content', value)    
    
    def prepare_content(self, value):
        # get the PGP field
        pgp_field = self.get_content_field()
            
        if not self._pgp__object_or_class and isinstance(pgp_field, AutoPGPTextField):
            # get the obj or at least model this content belongs to
            self._pgp__object_or_class = getattr(self, pgpcontent_settings.OBJECT_CONTENT_MODEL__OBJECT_GETTER)
            if self._pgp__object_or_class is None:                
                # get the GenericObject field and get at least the class
                meta    =   self.__class__._meta
                for field in meta.local_fields: # TODO: just meta.fields?
                    if field.attname == pgpcontent_settings.OBJECT_CONTENT_MODEL__OBJECT_GETTER:
                        if hasattr(field, '_get_model_from_obj'):
                            # model_registry.generic.GenericForeignKey
                            self._pgp__object_or_class = field._get_model_from_obj()
                        elif hasattr(field, 'get_content_type'):                            
                            content_type = getattr(self, field.ct_field)
                            if content_type != None:
                                self._pgp__object_or_class = field.get_content_type(content_type).model_class()
                    
        # let the field decide whether to encrypt or not at this point
        value = pgp_field.conditional_encrypt_value(value, self._pgp__object_or_class)
        return value
    
    def has_content(self, ):
        return bool(self.content)
    
    def __str__(self):
        return self.get_content()