# -*- coding: utf-8 -*-
from django import forms


class UserFormMixin(forms.Form):
    """Form mixin that puts the user on the form object."""

    def __init__(self, user=None, *args, **kwargs):
        if not hasattr(self, 'user'):
            if user is None:
                raise Exception('user is required for this form.')

            self.user = user

        super(UserFormMixin, self).__init__(*args, **kwargs)


class UserConnectionsFormMixin(UserFormMixin, forms.Form):
    """Form mixin that puts the user on the form object."""

    def __init__(self, user_connections=None, *args, **kwargs):
        if not hasattr(self, 'user_connections'):
            if user_connections is None:
                raise Exception('user connections are required for this form.')

            self.user_connections = user_connections

        super(UserConnectionsFormMixin, self).__init__(*args, **kwargs)


def get_user_connection_choices(user, user_connections, exclude_user_ids=None):
    """
    Gets the list of user you have connections to and returns in a list of
    tuples where the first index is the connection token and the second index
    is the users name sorted by users name.

    :param user: the authenticated user
    :param user_connections: the list or queryset of user connections
    :param exclude_user_ids: list of user ids to exclude from the list

    [
        (CONNECTION_TOKEN, USERS_FULL_NAME)
    ]


    """
    if exclude_user_ids is None:
        exclude_user_ids = []

    connections = []

    for conn in user_connections:
        conn_user = conn.get_connected_user(user)
        if conn_user.id in exclude_user_ids:
            continue

        connections.append((conn.token, conn_user.get_full_name()))

    connections.sort(key=lambda k: k[1])
    return connections
