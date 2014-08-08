from __future__ import unicode_literals

from django import template


register = template.Library()


@register.filter
def get_connected_user(user_connection, auth_user):
    """Gets the user the authenticated user is connected with."""
    if not user_connection:
        return None

    return user_connection.get_connected_user(auth_user)
