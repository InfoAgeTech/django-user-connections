from django_user_connections.managers import UserConnectionManager \
                                          as BaseUserConnectionManager


class UserConnectionManager(BaseUserConnectionManager):
    """Test manager for overriding the Notification's manager."""

    def my_new_manager_method(self):
        return 'works'
