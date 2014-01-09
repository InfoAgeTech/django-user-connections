# -*- coding: utf-8 -*-
from django.core.exceptions import ValidationError
from django.forms.fields import ChoiceField
from django.forms.fields import MultipleChoiceField
from django.forms.widgets import CheckboxSelectMultiple
from django.utils.six import string_types
from django.utils.translation import ugettext as _


class BaseUserConnectionFieldMixin(object):
    """Does all the leg work for figuring out which user connection choices
    to display when the field is rendered.
    """

    def __init__(self, user_connections=None, user=None,
                 exclude_user_ids=None, include_user_choice=False,
                 *args, **kwargs):
        """
        :param user_connections: iterable of user connections
        :param user: this is the user the connections are for.
        :param exclude_user_ids: a list of user ids to exclude from the field.
        :param include_user_choice: boolean indicating if `user` should be
            added as the first choice option.
        """
        self.include_user_choice = include_user_choice

        super(BaseUserConnectionFieldMixin, self).__init__(*args, **kwargs)
        self.exclude_user_ids = exclude_user_ids
        self.user = user
        self.user_connections = user_connections

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
            self.choices = self.get_user_connection_choices()
        else:
            self.choices = ()

        if self.include_user_choice:
            self.choices.insert(0, ('self', _('Me')))

    def get_user_connection_choices(self):
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
        if self.exclude_user_ids is None:
            exclude_user_ids = []
        else:
            exclude_user_ids = self.exclude_user_ids

        connections = []

        for conn in self.user_connections:
            conn_user = conn.get_connected_user(self.user)
            if conn_user.id in exclude_user_ids:
                continue

            connections.append((conn.token, conn_user.get_full_name()))

        connections.sort(key=lambda k: k[1])
        return connections

    def user_connection_tokens_to_users(self, selected_tokens):
        """Takes the selected user tokens and returns the users associated with the
        connection tokens.

        :param user: this is the authenticated user.
        :param selected_tokens: list of selected user tokens.
        :params user_connections: the list of user connections to pull the users
            from.
        """
        if not selected_tokens or not self.user_connections:
            return []

        return [c.get_connected_user(self.user) for c in self.user_connections
                if c.token in selected_tokens]

    def get_user_by_token(self, token):
        """Gets the user from the user_connections by token."""
        if not token or not self.user_connections:
            return None

        for connection in self.user_connections:
            if connection.token == token:
                return connection.get_connected_user(self.user)

        return None

    def get_token_by_user_id(self, user_id):
        """Gets a connection token by a user's id. If the user_id == self.user
        then this returns 'self' as the initial.
        """
        if not user_id or not self.user_connections:
            return None

        if self.user and self.user.id == user_id:
            return 'self'

        for connection in self.user_connections:
            if user_id in connection.user_ids:
                return connection.token

        return None

    def get_token_by_user(self, user):
        """Gets a conenction token for a user."""
        return self.get_token_by_user_id(user_id=user.id)


class BaseUserConnectionChoiceField(BaseUserConnectionFieldMixin):

    def __init__(self, empty_label='-----------', *args, **kwargs):
        """
        :param empty_label: the text to display for an empty option on a choice
            field if a field is not required.
        """
        self.empty_label = empty_label

        super(BaseUserConnectionChoiceField, self).__init__(*args, **kwargs)

    def _update_choices(self):
        super(BaseUserConnectionChoiceField, self)._update_choices()

        if not self.required and self.empty_label != None:
            self.choices.insert(0, ('', self.empty_label))


class UserConnectionChoiceField(BaseUserConnectionChoiceField, ChoiceField):
    """Builds a choice fields based on an iterable of user connections.

    When using this field, it's best to also add the UserConnectionsFormMixin
    to the form class as well. That way each UserConnection field will
    correctly display the list of users available.
    """

    def __init__(self, empty_label=u'-- Select User --', *args, **kwargs):
        """
        :param empty_label: the text to display for an empty option on a choice
            field if a field is not required.
        """
        super(UserConnectionChoiceField, self).__init__(empty_label=empty_label,
                                                        *args,
                                                        **kwargs)

    def clean(self, value):
        """Returns the user object or None if not found."""
        if value == 'self':
            return self.user

        return self.get_user_by_token(token=value)

    def validate(self, value):
        if value and value != 'self':
            user = self.get_user_by_token(token=value)

            if not user:
                raise ValidationError('No connection found with token '
                                      '{0}.'.format(value))

        super(UserConnectionChoiceField, self).validate(value)

    def _get_initial(self):
        return self._initial

    def _set_initial(self, value):
        if isinstance(value, int):
            if self.user and self.user.id == value:
                self._initial = 'self'
            else:
                # It's a user id, get the user from the user connections
                self._initial = self.get_token_by_user_id(value)
        elif value and not isinstance(value, string_types):

            # Try getting from a user
            try:
                self._initial = self.get_token_by_user(value)
            except:
                self._initial = value
        elif value == None:
            self._initial = 'self'
        else:
            self._initial = value

    initial = property(_get_initial, _set_initial)


class UserConnectionsMultipleChoiceField(BaseUserConnectionChoiceField,
                                         MultipleChoiceField):
    """Builds a multiple choice fields based on an iterable of user
    connections.

    When using this field, it's best to also add the UserConnectionsFormMixin
    to the form class as well. That way each UserConnection field will
    correctly display the list of users available.
    """

    widget = CheckboxSelectMultiple

    def clean(self, value):
        user_tokens = super(UserConnectionsMultipleChoiceField,
                            self).clean(value)
        return self.user_connection_tokens_to_users(
                                                selected_tokens=user_tokens)
