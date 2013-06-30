# -*- coding: utf-8 -*-

from django_tools.managers import CommonManager
from django_tools.managers import TokenManager


class ConnectionManager(TokenManager, CommonManager):

    def create(self, created_user, with_user, **kwargs):
        """Creates a Connection.
        
        
        :param created: the user of the person creating the connection.
        :param with_user: the user id of the person being requested 
            to connect
        :param status: the status of the connection. Default is 'pending'.
           
        """
        # First need to make sure the connection doesn't already exist.
        conn = self.get_for_users(user_id_1=created.id, user_id_2=with_user.id)
        if conn:
            # should probably return an error here.  Should be using get_or_create
            return conn

        conn = super(ConnectionManager, self).create(created_user=created_user,
                                                     last_modified_user=created_user,
                                                     **kwargs)
        conn.users.add(created, with_user)
        return conn

    def get_or_create(self, created_user, with_user, **kwargs):
        """Gets or creates a connection.
        
        :param created: the user creating the connection.
        :param with_user: the user to get or create the connection with.
        
        """
        conn = self.get_for_users(user_id_1=created.id, user_id_2=with_user.id)

        if conn:
            return conn, False

        return self.create(created_user=created_user, with_user=with_user), True

    def get_for_users(self, user_id_1, user_id_2):
        """Gets a connection between two users.
        
        :returns: single connection object between the two users. 
        """
        # Can I instead do:
        try:
            return (self.filter(users__id=user_id_1)
                        .filter(users__id=user_id_2).get())
        except self.model.DoesNotExist:
            return None

    def get_by_user(self, user, **kwargs):
        """Gets all connections for a user for both connections this
        user created as well as connections that were created by other with
        this user.
        
        """
        return self.get_by_user_id(user_id=user.id, **kwargs)

    def get_by_user_id(self, user_id, **kwargs):
        """Gets all connections for a user by a user id for both connections this
        user created as well as connections that were created by other  with
        this user.
        
        """
        return self.filter(users__id=user_id, **kwargs)

    def get_user_ids(self, user_id):
        """Gets a set of all the user ids this user has connections with."""
        connections = self.get_by_user_id(user_id)

        if not connections:
            return []

        conn_user_ids = []
        for c in connections:
            # A connection can either be created by this user or another user
            # so add both created_id and with_user_id to list.  Either can be
            # valid connection user id.
            conn_user_ids.extend([c.with_user.id, c.created.id])

        conn_user_ids = set(conn_user_ids)
        conn_user_ids.remove(user_id)
        return conn_user_ids
