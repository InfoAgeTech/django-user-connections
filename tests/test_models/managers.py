from __future__ import unicode_literals

from user_connections.managers import UserConnectionManager \
                                          as BaseUserConnectionManager


class UserConnectionManager(BaseUserConnectionManager):
    """Test manager for overriding the UserConnection's manager."""

    def my_new_manager_method(self):
        return 'works'
