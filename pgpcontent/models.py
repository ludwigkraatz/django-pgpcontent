from django.db.models import fields
from django.db.models.fields import related

from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType

from pgpcontent.abstract_models import *
from pgpcontent.settings import pgpcontent_settings

class ObjectContent(abstractPGPContent):
    class Meta(abstractPGPContent.Meta):
        swappable = 'PGP_CONTENT__OBJECT_CONTENT_MODEL'    
        unique_together = ( ('object_id', 'content_type'), )
    
    object_id           =   fields.IntegerField(null=False, blank=False)
    content_type        =   related.ForeignKey(ContentType, null=False, blank=False)
    
    # Any ObjectContent Model needs an object getter which returns the specified Object
    pgpcontent_settings.OBJECT_CONTENT_MODEL__OBJECT_GETTER =   generic.GenericForeignKey('content_type', 'object_id')
    
