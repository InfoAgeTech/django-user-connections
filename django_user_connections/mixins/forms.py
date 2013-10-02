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


class UserConnectionsMultiSelectFormMixin(UserConnectionsFormMixin,
                                          forms.Form):
    """Form contains a field with a multi checkbox select for all the user
    connections.

    Note: This requires that the UserFormMixin be called prior to this being
    called.
    """

    selected_users = forms.MultipleChoiceField(required=False,
                                        widget=forms.CheckboxSelectMultiple)

    def __init__(self, *args, **kwargs):
        super(UserConnectionsMultiSelectFormMixin, self).__init__(*args,
                                                                  **kwargs)

        if self.user_connections:
            self.fields['selected_users'].choices = get_user_connection_choices(
                                        user=self.user,
                                        user_connections=self.user_connections)

    def clean(self):
        cleaned_data = super(UserConnectionsMultiSelectFormMixin, self).clean()

        user_tokens = cleaned_data.get('selected_users')

        if user_tokens:
            cleaned_data['selected_users'] = user_connection_tokens_to_users(
                user=self.user,
                selected_tokens=user_tokens,
                user_connections=self.user_connections)

        return cleaned_data


class UserConnectionSelectFormMixin(UserConnectionsFormMixin, forms.Form):
    """Form contains a select dropdown of all the user's connections.

    Note: This requires that the UserFormMixin be called prior to this being
    called.
    """

    selected_user = forms.ChoiceField()

    def __init__(self, *args, **kwargs):
        super(UserConnectionSelectFormMixin, self).__init__(*args, **kwargs)

        if self.user_connections:
            self.fields['selected_user'].choices = get_user_connection_choices(
                                        user=self.user,
                                        user_connections=self.user_connections)

    def clean(self):
        cleaned_data = super(UserConnectionSelectFormMixin, self).clean()
        cleaned_data['selected_user'] = get_user_by_token(
                                    user=self.user,
                                    token=cleaned_data.get('selected_user'),
                                    user_connections=self.user_connections)
        return cleaned_data


def get_user_connection_choices(user, user_connections, exclude_ids=None):
    """
    Gets the list of user you have connections to and returns in a list of
    tuples where the first index is the connection token and the second index
    is the users name sorted by users name.

    :param user: the authenticated user
    :param user_connections: the list or queryset of user connections
    :param exclude_ids: list of user ids to exclude from the list

    [
        (CONNECTION_TOKEN, USERS_FULL_NAME)
    ]


    """
    if exclude_ids is None:
        exclude_ids = []

    connections = []

    for conn in user_connections:
        conn_user = conn.get_connected_user(user)
        if conn_user.id in exclude_ids:
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
