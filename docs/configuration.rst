=============
Configuration
=============

Extending the UserConnection Model with Model Mixin Hooks
=========================================================
There are times when a generic 3rd party model doesn't quite give you all the functionality you'd like.  Things like project specific settings or adding helper functions like::

    def get_absolute_url(...)

This app give you the ability to add a mixin to the UserConnection model to alter it's behavior.

Creating the Model Mixin
------------------------
Create the mixin you want to apply to the UserConnection model::

    # my_user_connection_app/models.py
    from django.db import models
    
    class AbstractUserConnectionMixin(models.Model):
        """The abstract user connection model to add functionality to the
        UserConnection's model.
        """
    
        class Meta:
            abstract = True
        
        def get_absolute_url(self):
            return reverse('my_user_connection_url_name', args=[self.id])
        
        def my_new_method(self):
            # do something with the user connection object
            return 'works'

Configuring the Mixin
---------------------
In your django settings.py file, include the ``USER_CONNECTION_MODEL_MIXIN`` that points to your user connection model mixin::

    USER_CONNECTION_MODEL_MIXIN = 'my_user_connections_app.AbstractUserConnectionMixin'
    
Using the New Model
-------------------
Now that the mixin has been created and configured, let's use it::

    >>> from django_user_connections.models import UserConnection
    >>> n = UserConnection()
    >>> n.my_new_method()
    'works'

Using a Custom Model Manager
============================
There are also times when you want to customize a model manager, but don't want to create another concrete implementation or proxy model.  Here's how you extend or override the object manager model.

Creating the Model Manager
--------------------------
Create the manager you want to user for the UserConnection model::

    # my_user_connection_app/managers.py
    from django_user_connections.managers import UserConnectionManager


    class MyUserConnectionManager(UserConnectionManager):
        """Manager for overriding the UserConnection's manager."""

        def my_new_manager_method(self):
            return 'works'


Configuring the Manager
-----------------------
In your django settings.py file, include the ``USER_CONNECTION_MANAGER`` that points to user connection manager you want to use for the project::

    USER_CONNECTION_MANAGER = 'my_user_connections_app.managers.MyUserConnectionManager'
    
Using the New Manager
---------------------
Now that the manager has been created and configured, let's use it::
    
    >>> from django_user_connections.models import UserConnection
    >>> n = UserConnection.objects.my_new_manager_method()
    'works'

Extend the Model
================
If all this configuration still isn't to your liking, then you can simply extend the AbstractUserConnection model::

    # my_user_connection_app/models.py
    
    from django_user_connections.models import AbstractUserConnection
    
    class MyUserConnection(AbstractUserConnection):
        """Your concrete implementation of the user connection app."""
        # Do your stuff here