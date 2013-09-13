def get_content_model():
    from django.conf import settings
    from django.db.models.loading import get_model
    
    return get_model(*getattr(settings, 'PGP_CONTENT__OBJECT_CONTENT_MODEL', 'pgpcontent.ObjectContent').split('.'))
