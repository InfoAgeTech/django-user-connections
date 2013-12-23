# -*- coding: utf-8 -*-

from django_core.forms.mixins.users import UserFormMixin

from ..forms.fields import BaseUserConnectionFieldMixin


class UserConnectionsFormMixin(UserFormMixin):
    """Form mixin that puts the user on the form object."""

    def __init__(self, user_connections=None, exclude_user_ids=None, *args,
                 **kwargs):
        if not hasattr(self, 'user_connections'):
            if user_connections is None:
                raise Exception('user connections are required for this form.')

            self.user_connections = user_connections

        self.exclude_user_ids = exclude_user_ids

        super(UserConnectionsFormMixin, self).__init__(*args, **kwargs)

        # Updates any BaseUserConnectionFieldMixin fields with the user and
        # user_connections
        for key, field in self.fields.items():
            if isinstance(field, BaseUserConnectionFieldMixin):
                if self.user:
                    field.user = self.user

                if self.user_connections:
                    field.user_connections = self.user_connections

                if self.exclude_user_ids:
                    field.exclude_user_ids = self.exclude_user_ids

                field_initial = self.initial.get(key)

                if field_initial:
                    self.initial[key] = field.get_token_by_user_id(
                                                                field_initial)
