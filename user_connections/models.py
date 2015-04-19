from __future__ import unicode_literals

from django.conf import settings
from django.db import models
from django.db.models import F
from django_core.db.models import AbstractTokenModel
from django_core.db.models.mixins.base import AbstractBaseModel
from django_core.utils.loading import get_class_from_settings

from .constants import Status

try:
    AbstractUserConnectionMixin = get_class_from_settings(
        settings_key='USER_CONNECTION_MODEL_MIXIN')
except NotImplementedError:

    class PlaceholderModel(models.Model):
        """Placeholder model that does nothing."""
        class Meta:
            abstract = True

    AbstractUserConnectionMixin = PlaceholderModel

try:
    UserConnectionManager = get_class_from_settings(
        settings_key='USER_CONNECTION_MANAGER')
except NotImplementedError:
    from .managers import UserConnectionManager


class AbstractUserConnection(AbstractUserConnectionMixin, AbstractTokenModel,
                             AbstractBaseModel):
    """Abstract user connection model.

    :field status: status of the connection. Can be one of
        user_connections.constants.Status
    :field token: token shared between the two users
    :field user_ids: list of user ids who are connected. This assumes that at
        most 2 people are connected.
    :field activity_count: the total number of interactions between two users.
        This field becomes useful when you want to start sorting user
        connections by relevance.  The higher the activity count, the more
        likely these two users are interested in each other.
    """
    status = models.CharField(max_length=25,
                              default=Status.PENDING,
                              choices=Status.CHOICES)
    with_user = models.ForeignKey(settings.AUTH_USER_MODEL,
                                  related_name='connections',
                                  db_index=True)
    activity_count = models.IntegerField(default=1)
    objects = UserConnectionManager()

    @property
    def users(self):
        """Property field gettings the two users the connection is for."""
        return [self.created_user, self.with_user]

    @property
    def user_ids(self):
        """Gets the user ids of the two users connected."""
        return [self.created_user_id, self.with_user_id]

    class Meta:
        abstract = True
        index_together = (('created_user', 'with_user'),)
        ordering = ('-id',)

    def accept(self):
        """Accepts a user connection."""
        self.status = Status.ACCEPTED
        self.save()

    def decline(self):
        """Declines a user connection."""
        self.status = Status.DECLINED
        self.save()

    def inactivate(self):
        """Inactivate a user connection."""
        self.status = Status.INACTIVE
        self.save()

    def is_accepted(self):
        """Boolean indicating if the status is accepted."""
        return self.status == Status.ACCEPTED

    def is_pending(self):
        """Boolean indicating if the status is pending."""
        return self.status == Status.PENDING

    def is_declined(self):
        """Boolean indicating if the status is declined."""
        return self.status == Status.DECLINED

    def is_inactive(self):
        """Boolean indicating if the status is inactive."""
        return self.status == Status.INACTIVE

    def increment_activity_count(self):
        """Increments total activity count for the connection between two
        users.
        """
        self.activity_count = F('activity_count') + 1
        self.save()
        return True

    @classmethod
    def increment_activity_count_by_users(cls, user_id_1, user_id_2):
        """Increments total activity count for the connection between two
        users.

        :param user_id_1: user id of the first user in a connection
        :param user_id_2: user id of the second user in a connection

        """
        conn = cls.objects.get_for_users(user_id_1, user_id_2)

        if not conn:
            return False

        conn.increment_activity_count()
        return True

    def get_connected_user(self, user):
        """Gets the user who's not the user param passed in.

        :param user: return the user who's not this user.
        """
        if user not in self.users:
            return None

        return self.users[1] if self.users[0] == user else self.users[0]


class UserConnection(AbstractUserConnection):
    """Concrete class for user connections."""
