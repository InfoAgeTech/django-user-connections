# -*- coding: utf-8 -*-
from django_user_connections.models import Connection
from mongo_testing.auth import User
from mongo_testing.testcase import MongoTestCase
from python_tools.random_utils import random_alphanum_id

class ConnectionTests(MongoTestCase):

    @classmethod
    def setUpClass(cls):
        """Run once per test case"""
        super(ConnectionTests, cls).setUpClass()
        cls.usr = User.objects.create(id=random_alphanum_id())

    def test_add_connection(self):
        """Test for adding a connection between 2 users."""
        usr_2 = User.objects.create(id=random_alphanum_id())

        conn = Connection.add(creating_user=self.usr,
                              connect_with_user_id=usr_2.id,
                              status=Connection.STATUS.PENDING)

        self.assertEquals(conn.total_activity_count, 1)
        self.assertEquals(conn.status, Connection.STATUS.PENDING)
        self.assertEquals(len(conn.user_ids), 2)
        self.assertTrue(self.usr.id in conn.user_ids)
        self.assertTrue(usr_2.id in conn.user_ids)

    def test_accept_connection(self):
        """Test for accepting a connection."""
        usr_2 = User.objects.create(id=random_alphanum_id())

        conn = Connection.add(creating_user=self.usr,
                              connect_with_user_id=usr_2.id,
                              status=Connection.STATUS.PENDING)

        self.assertEquals(conn.status, Connection.STATUS.PENDING)
        conn.accept()
        self.assertEquals(conn.status, Connection.STATUS.ACCEPTED)

    def test_decline_connection(self):
        """Test for declining a connection."""
        usr_2 = User.objects.create(id=random_alphanum_id())

        conn = Connection.add(creating_user=self.usr,
                              connect_with_user_id=usr_2.id,
                              status=Connection.STATUS.PENDING)

        self.assertEquals(conn.status, Connection.STATUS.PENDING)
        conn.decline()
        self.assertEquals(conn.status, Connection.STATUS.DECLINED)

    def test_incremement_activity_count(self):
        """Test for incrementing the total activity count for a connection."""
        usr_2 = User.objects.create(id=random_alphanum_id())

        conn = Connection.add(creating_user=self.usr,
                              connect_with_user_id=usr_2.id,
                              status=Connection.STATUS.PENDING)

        self.assertEquals(conn.total_activity_count, 1)
        conn.increment_activity_count()
        self.assertEquals(conn.total_activity_count, 2)

    def test_incremement_activity_count_by_users(self):
        """Test for incrementing the total activity count for a connection."""
        usr_2 = User.objects.create(id=random_alphanum_id())

        conn = Connection.add(creating_user=self.usr,
                              connect_with_user_id=usr_2.id,
                              status=Connection.STATUS.PENDING)

        self.assertEquals(conn.total_activity_count, 1)
        Connection.increment_activity_count_by_users(user_id_1=self.usr.id,
                                                     user_id_2=usr_2.id)
        conn.reload()
        self.assertEquals(conn.total_activity_count, 2)

    def test_get_by_user_id(self):
        """Test for getting connections by a specific user id."""
        usr_2 = User.objects.create(id=random_alphanum_id())
        user_ids = [random_alphanum_id() for i in range(10)]

        for user_id in user_ids:
            conn = Connection.add(creating_user=usr_2,
                                  connect_with_user_id=user_id,
                                  status=Connection.STATUS.PENDING)

        connections = Connection.get_by_user_id(user_id=usr_2.id)
        self.assertEquals(len(connections), 10)

    def test_get_connection_by_user_ids(self):
        """Test for getting a connection between 2 users."""
        usr_2 = User.objects.create(id=random_alphanum_id())

        conn = Connection.add(creating_user=self.usr,
                              connect_with_user_id=usr_2.id,
                              status=Connection.STATUS.PENDING)

        conn_1 = Connection.get(user_id_1=self.usr.id, user_id_2=usr_2.id)
        self.assertEquals(conn, conn_1)
        conn_2 = Connection.get(user_id_1=usr_2.id, user_id_2=self.usr.id)
        self.assertEquals(conn, conn_2)

    def test_get_for_user_id(self):
        """Test for retrieving the id of the user the connection is intended for.
        """
        usr_2 = User.objects.create(id=random_alphanum_id())

        conn = Connection.add(creating_user=self.usr,
                              connect_with_user_id=usr_2.id,
                              status=Connection.STATUS.PENDING)

        self.assertEquals(conn.get_for_user_id(), usr_2.id)


    def test_get_by_token(self):
        """Test for getting a connection by a token."""
        usr_2 = User.objects.create(id=random_alphanum_id())

        conn = Connection.add(creating_user=self.usr,
                              connect_with_user_id=usr_2.id,
                              status=Connection.STATUS.PENDING)

        conn_2 = Connection.get_by_token(token=conn.token)

        self.assertEquals(conn, conn_2)

    def test_get_next_token(self):
        """Test for getting the next token."""
        token = Connection.get_next_token(length=20)
        self.assertEquals(len(token), 20)
