# -*- coding: utf-8 -*-
from django.core.exceptions import ImproperlyConfigured


def get_user_connection_model():
    """Return the UserConnection model that is active in this project.

    This is the same pattern user for django's "get_user_model()" method. To
    allow you to set the model instance to a different model subclass.
    """
    from django.conf import settings
    from django.db.models import get_model

    if not hasattr(settings, 'NOTIFICATION_MODEL'):
        from .models import UserConnection
        return UserConnection

    try:
        app_label, model_name = settings.USER_CONNECTION_MODEL.split('.')
    except ValueError:
        raise ImproperlyConfigured("USER_CONNECTION_MODEL must be of the form 'app_label.model_name'")

    user_connection_model = get_model(app_label, model_name)

    if user_connection_model is None:
        raise ImproperlyConfigured("USER_CONNECTION_MODEL refers to model '%s' that has not been installed" % settings.USER_CONNECTION_MODEL)

    return user_connection_model
