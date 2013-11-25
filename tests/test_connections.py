# -*- coding: utf-8 -*-

from django.contrib.auth import get_user_model
from django.test.testcases import TestCase
from django_testing.user_utils import create_user
from django_user_connections import get_user_connection_model
from django_user_connections.constants import Status


User = get_user_model()
UserConnection = get_user_connection_model()


class ConnectionTestCase(TestCase):

    @classmethod
    def setUpClass(cls):
        super(TestCase, cls).setUpClass()
        cls.user = create_user()

    def test_accept_connection(self):
        """Test for accepting a connection."""
        user_2 = create_user()

        conn = UserConnection.objects.create(created_user=self.user,
                                             with_user=user_2,
                                             status=Status.PENDING)

        self.assertEqual(conn.status, Status.PENDING)
        conn.accept()
        self.assertEqual(conn.status, Status.ACCEPTED)

    def test_decline_connection(self):
        """Test for declining a connection."""
        user_2 = create_user()

        conn = UserConnection.objects.create(created_user=self.user,
                                             with_user=user_2,
                                             status=Status.PENDING)

        self.assertEqual(conn.status, Status.PENDING)
        conn.decline()
        self.assertEqual(conn.status, Status.DECLINED)

    def test_incremement_activity_count(self):
        """Test for incrementing the total activity count for a connection."""
        user_2 = create_user()

        conn = UserConnection.objects.create(created_user=self.user,
                                         with_user=user_2)

        self.assertEqual(conn.activity_count, 1)
        conn.increment_activity_count()

        conn = UserConnection.objects.get(id=conn.id)
        self.assertEqual(conn.activity_count, 2)

    def test_incremement_activity_count_by_users(self):
        """Test for incrementing the total activity count for a connection."""
        user_2 = create_user()

        conn = UserConnection.objects.create(created_user=self.user,
                                         with_user=user_2)

        self.assertEqual(conn.activity_count, 1)
        UserConnection.increment_activity_count_by_users(user_id_1=self.user.id,
                                                     user_id_2=user_2.id)

        conn = UserConnection.objects.get(id=conn.id)
        self.assertEqual(conn.activity_count, 2)

    def test_get_by_user_id(self):
        """Test for getting connections by a specific user id."""
        user_2 = create_user()
        users = [create_user() for i in range(10)]

        for user in users:
            conn = UserConnection.objects.create(created_user=user_2,
                                             with_user=user)

        connections = UserConnection.objects.get_by_user_id(user_id=user_2.id)
        self.assertEqual(len(connections), 10)

    def test_get_connection_by_user_ids(self):
        """Test for getting a connection between 2 users."""
        user_2 = create_user()

        conn = UserConnection.objects.create(created_user=self.user,
                                         with_user=user_2,
                                         status=Status.PENDING)

        conn_1 = UserConnection.objects.get_for_users(user_1=self.user, user_2=user_2)
        self.assertEqual(conn, conn_1)
        conn_2 = UserConnection.objects.get_for_users(user_1=user_2, user_2=self.user)
        self.assertEqual(conn, conn_2)

    def test_get_by_token(self):
        """Test for getting a connection by a token."""
        user_2 = create_user()

        conn = UserConnection.objects.create(created_user=self.user,
                                         with_user=user_2,
                                         status=Status.PENDING)

        conn_2 = UserConnection.objects.get_by_token(token=conn.token)

        self.assertEqual(conn, conn_2)

    def test_get_next_token(self):
        """Test for getting the next token."""
        token = UserConnection.objects.get_next_token(length=20)
        self.assertEqual(len(token), 20)

    def test_delete_connection(self):
        """Testing deleting a connection."""
        user_2 = create_user()
        c = UserConnection.objects.create(created_user=self.user,
                                      with_user=user_2,
                                      status=Status.ACCEPTED)
        c.delete()

        conn_1 = UserConnection.objects.get_for_users(user_1=self.user,
                                                  user_2=user_2)
        self.assertIsNone(conn_1)

    def test_get_connected_user(self):
        """Test getting the user the connection is with. Could be the connected
        user or the with_user.
        """
        user_2 = create_user()
        c = UserConnection.objects.create(created_user=self.user,
                                          with_user=user_2,
                                          status=Status.ACCEPTED)

        self.assertEqual(c.get_connected_user(self.user), user_2)
        self.assertEqual(c.get_connected_user(user_2), self.user)

        user_3 = create_user()
        self.assertIsNone(c.get_connected_user(user_3))
