# -*- coding: utf-8 -*-
from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import F

from django_core.models import AbstractBaseModel

from .constants import Status
from .managers import UserConnectionManager

User = get_user_model()


class UserConnection(AbstractBaseModel):
    """
    Fields
    ======
    
    * status = status of the connection. Can be one of the following:
        accepted = the connection has been accepted
        pending = pending connection
    * token = token shared between the two users
    * user_ids  = list of user ids who are connected. This assumes that at most  
        2 people are connected.
    * email_sent = boolean indicating if a connection email was sent once
        a connection became accepted.
    * activity_count = the total number of interactions between two users.
    """

    status = models.CharField(max_length=25,
                              default=Status.PENDING,
                              choices=Status.CHOICES)
    with_user = models.ForeignKey(User, db_index=True)
    token = models.CharField(max_length=50, db_index=True)
    email_sent = models.BooleanField(default=False)
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
        # TODO: might want an index_together on created_user and with_user
        ordering = ('-created_dttm',)

    def save(self, *args, **kwargs):

        if not self.token:
            self.token = self.__class__.objects.get_next_token()

        return super(UserConnection, self).save(*args, **kwargs)

    def accept(self):
        """Accepts a user connection."""
        self.status = Status.ACCEPTED
        self.save()

    def decline(self):
        """Declines a user connection."""
        self.status = Status.DECLINED
        self.save()

    def increment_activity_count(self):
        """Increments total activity count for the connection between two users.
        """
        self.activity_count = F('activity_count') + 1
        self.save()
        return True

    @classmethod
    def increment_activity_count_by_users(cls, user_id_1, user_id_2):
        """Increments total activity count for the connection between two users.
        
        :param user_id_1: user id of the first user in a connection
        :param user_id_2: user id of the second user in a connection
        
        """
        conn = cls.objects.get_for_users(user_id_1, user_id_2)

        if not conn:
            return False

        conn.increment_activity_count()
        return True

    def get_for_user_id(self):
        """Gets the user id this connection is intended for.  This is the user 
        that did NOT create the connection.
        
        """
        return self.with_user_id
