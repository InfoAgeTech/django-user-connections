# -*- coding: utf-8 -*-
from django.core.exceptions import ValidationError
from django.forms.fields import ChoiceField
from django.forms.fields import MultipleChoiceField
from django.forms.widgets import CheckboxSelectMultiple


class BaseUserConnectionFieldMixin(object):
    """Does all the leg work for figuring out which user connection choices
    to display when the field is rendered.
    """

    def __init__(self, user_connections=None, user=None,
                 exclude_user_ids=None, *args, **kwargs):
        """
        :param user_connections: iterable of user connections
        :param user: this is the user the connections are for.
        :param exclude_user_ids: a list of user ids to exclude from the field.
        """
        self.exclude_user_ids = exclude_user_ids
        self.user = user
        self.user_connections = user_connections
        super(BaseUserConnectionFieldMixin, self).__init__(*args, **kwargs)

    def _get_user_connections(self):
        return getattr(self, '_user_connections', None)

    def _set_user_connections(self, value):
        self._user_connections = value
        self._update_choices()

    user_connections = property(_get_user_connections, _set_user_connections)

    def _get_exclude_user_ids(self):
        return getattr(self, '_exclude_user_ids', None)

    def _set_exclude_user_ids(self, value):
        self._exclude_user_ids = value
        self._update_choices()

    exclude_user_ids = property(_get_exclude_user_ids, _set_exclude_user_ids)

    def _get_user(self):
        return getattr(self, '_user', None)

    def _set_user(self, value):
        self._user = value
        self._update_choices()

    user = property(_get_user, _set_user)

    def _update_choices(self):
        if self.user and self._user_connections:
            self.choices = get_user_connection_choices(
                                    user=self.user,
                                    user_connections=self._user_connections,
                                    exclude_user_ids=self.exclude_user_ids)
        else:
            self.choices = ()


class UserConnectionChoiceField(BaseUserConnectionFieldMixin, ChoiceField):
    """Builds a choice fields based on an iterable of user connections."""

    def clean(self, value):
        """Returns the user object or None if not found."""
        if value == 'self':
            return self.user

        return get_user_by_token(user=self.user,
                                 token=value,
                                 user_connections=self.user_connections)

    def validate(self, value):
        if value and value != 'self':
            user = get_user_by_token(user=self.user,
                                 token=value,
                                 user_connections=self.user_connections)

            if not user:
                raise ValidationError('No connection found with token '
                                      '{0}.'.format(value))

        super(UserConnectionChoiceField, self).validate(value)


class UserConnectionsMultipleChoiceField(BaseUserConnectionFieldMixin,
                                         MultipleChoiceField):

    widget = CheckboxSelectMultiple

    def clean(self, value):
        user_tokens = super(UserConnectionsMultipleChoiceField,
                            self).clean(value)
        return user_connection_tokens_to_users(
                                        user=self.user,
                                        selected_tokens=user_tokens,
                                        user_connections=self.user_connections)


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


def user_connection_tokens_to_users(user, selected_tokens, user_connections):
    """Takes the selected user tokens and returns the users associated with the
    connection tokens.

    :param user: this is the authenticated user.
    :param selected_tokens: list of selected user tokens.
    :params user_connections: the list of user connections to pull the users
        from.
    """
    return [c.get_connected_user(user) for c in user_connections
            if c.token in selected_tokens]


def get_user_by_token(user, token, user_connections):
    """Gets the user from the user_connections by token."""
    for connection in user_connections:
        if connection.token == token:
            return connection.get_connected_user(user)

    return None
