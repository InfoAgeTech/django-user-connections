========
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