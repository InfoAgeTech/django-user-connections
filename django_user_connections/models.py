# -*- coding: utf-8 -*-
from django.contrib.auth import get_user_model
# from django.core.urlresolvers import reverse
from django.db import models
from django.db.models import F
from django.db.models.query_utils import Q
from django.http import Http404
from django_tools.models import AbstractBaseModel
from python_tools.random_utils import random_alphanum_id

User = get_user_model()


class Connection(AbstractBaseModel):
    """
    Attributes:
    
    status = status. Can be one of the following:
        accepted = the connection has been accepted
        pending = pending connection
    token = token shared between the two users
    user_ids  = list of user ids who are connected. This assumes that at most 2 people
        are connected.
    email_sent = boolean indicating if a connection email was sent once
        a connection became accepted.
    total_activity_count = the total number of interactions between two users.
    """
    class STATUS:
        ACCEPTED = 'accepted'
        DECLINED = 'declined'
        PENDING = 'pending'

        CHOICES = (
            (ACCEPTED, 'Accepted'),
            (DECLINED, 'Declined'),
            (PENDING, 'Pending')
        )

    status = models.CharField(max_length=25, choices=STATUS.CHOICES)
    with_user = models.ForeignKey(User)
    token = models.CharField(max_length=50)
    email_sent = models.BooleanField(default=False)
    total_activity_count = models.IntegerField(default=0)

#    meta = {'collection': 'connections',
#            'indexes': ['token', 'user_ids'],
#            'ordering': ['-created_dttm']

    def save(self, *args, **kwargs):
        if not self.token:
            self.token = Connection.get_next_token()

        super(Connection, self).save(*args, **kwargs)

    @classmethod
    def add(cls, creating_user, connect_with_user, status=STATUS.PENDING):
        """Adds a connection between two users.
        
        :param creating_user: the user of the person creating the connection.
        :param connect_with_user_id: the user id of the person being requested 
            to connect
        :param status: the status of the connection.  Should probably be in
            'pending' status until the user_id user accepts the connection.
            
        """
        conn = cls()
        conn.status = status
        conn.with_user = connect_with_user
        conn.created = creating_user
        conn.total_activity_count = 1
        conn.save()
        return conn

    def accept(self):
        """Accepts a user connection."""
        self.status = Connection.STATUS.ACCEPTED
        self.save()

    def decline(self):
        """Declines a user connection."""
        self.status = Connection.STATUS.DECLINED
        self.save()

#    @classmethod
    def increment_activity_count(self):
#    def increment_activity_count_by_users(self):  # cls, user_id_1, user_id_2):
        """Increments total activity count for the connection.  
        
        This is a quick operation that doesn't wait for a response from mongodb 
        so there a chance it could fail.  However, that's ok since we're not 
        looking for exact numbers here, just rough estimates.
        
        :param user_id_1: user id of the first user in a connection
        :param user_id_2: user id of the second user in a connection
        
        """
#        user_ids = [user_id_1, user_id_2]
#        cls.objects(user_ids__all=user_ids).update_one(inc__total_activity_count=1,
#                                                       safe_update=False)
        self.total_activity_count = F('total_activity_count') + 1

    def get_for_user_id(self):
        """Gets the user id this connection is intended for.  This is the user 
        that did NOT create the connection.
        
        """
        return self.with_user.id

    @classmethod
    def get(cls, user_id_1, user_id_2):
        """Gets a connection between two users."""
        try:
#            return cls.objects.get(user_ids__all=[user_id_1, user_id_2])
            return cls.objects.get((Q(with_user=user_id_1) and Q(created=user_id_2)) |
                                   (Q(with_user=user_id_2) and Q(created=user_id_1)))
        except cls.DoesNotExist:
            return None

    @classmethod
    def get_by_user_id(cls, user_id):
        """Gets all connections for a user by a user id for both connections this
        user created as well as connections that were created by other  with
        this user.
        
        """
        return cls.objects.filter(Q(with_user=user_id) | Q(created=user_id))

    @classmethod
    def get_user_ids(cls, user_id):
        """Gets a set of all the user ids this user has connections with."""
        connections = cls.get_by_user_id(user_id)
        if not connections:
            return set()

        conn_user_ids = []
        for c in connections:
            # A connection can either be created by this user or another user
            # so add both created_id and with_user_id to list.  Either can be
            # valid connection user id.
            conn_user_ids.extend([c.with_user.id, c.created.id])

        conn_user_ids = set(conn_user_ids)
        conn_user_ids.remove(user_id)
        return conn_user_ids

    @classmethod
    def get_by_token(cls, token):
        try:
            return cls.objects.get(token=token)
        except cls.DoesNotExist:
            return None

    @classmethod
    def get_by_token_or_404(cls, token):
        c = cls.get_by_token(token)
        if not c:
            raise Http404

        return c

    @classmethod
    def get_next_token(cls, length=20):
        """Gets the next available token.  This method ensures the token is 
        unique.
        
        """
        token = random_alphanum_id(length)
        while True:
            conn = cls.get_by_token(token=token)
            if not conn:
                return token

            token = random_alphanum_id(length)

#    def get_absolute_url(self):
#        return reverse('connection_view', args=[self.id])
