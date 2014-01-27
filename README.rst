NOTE: This is not stable yet and will likely change!  Please don't use in production until the 1.0 release.

.. image:: https://badge.fury.io/py/django-user-connections.png
    :target: http://badge.fury.io/py/django-user-connections
.. image:: https://travis-ci.org/InfoAgeTech/django-user-connections.png?branch=master
    :target: http://travis-ci.org/InfoAgeTech/django-user-connections
.. image:: https://coveralls.io/repos/InfoAgeTech/django-user-connections/badge.png
    :target: https://coveralls.io/r/InfoAgeTech/django-user-connections
.. image:: https://pypip.in/license/django-user-connections/badge.png
    :target: https://pypi.python.org/pypi/django-user-connections/

==============================================
django-user-connections |travisci| |coveralls|
==============================================
django-user-connections is a python module written for django that handles user connections.

Docs
====

http://django-user-connections.readthedocs.org

Intallation
===========
Install the app:: 

   pip install django-user-connections

Dependencies
============
* `django-core <https://github.com/InfoAgeTech/django-core>`_
TODO

Examples
========
Below are some basic examples on how to use django-user-connections::

    >>> from django.contrib.auth import get_user_model
    >>> from django_user_connections.models import UserConnection
    >>>
    >>> User = get_user_model()
    >>> user_1 = User.objects.create_user(username='hello')
    >>> user_2 = User.objects.create_user(username='world')
    >>>
    >>> conn = UserConnection.objects.create(created_user=user_1,
    ...                                      with_user=user_2)
    >>> conn.status
    'PENDING'
    >>> user_connection = UserConnection.objects.get_for_users(user_1=user_1,
    ...                                                        user_2=user_2)
    >>> conn == user_connection
    True


Extending the UserConnection Model
==================================
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

Tests
=====
From the ``tests`` directory where the manage.py file is, run::

   python manage.py test
