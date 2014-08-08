from __future__ import unicode_literals

from django.contrib.auth import get_user_model
from django.test import TestCase
from django_testing.user_utils import create_user

from user_connections import get_user_connection_model
from user_connections.constants import Status


User = get_user_model()
UserConnection = get_user_connection_model()


class ConnectionManagerTestCase(TestCase):

    @classmethod
    def setUpClass(cls):
        super(TestCase, cls).setUpClass()
        cls.user = create_user()

    def test_create_connection_pending(self):
        """Test for adding a pending connection between 2 users."""
        user_2 = create_user()

        conn = UserConnection.objects.create(created_user=self.user,
                                             with_user=user_2,
                                             status=Status.PENDING)

        self.assertEqual(conn.activity_count, 1)
        self.assertEqual(conn.status, Status.PENDING)
        self.assertEqual(conn.created_user, self.user)

        users = conn.users
        self.assertEqual(len(users), 2)
        self.assertTrue(self.user in users)
        self.assertTrue(user_2 in users)

    def test_create_connection_accepted(self):
        """Test for adding an accepted connection between 2 users."""
        user_2 = create_user()

        conn = UserConnection.objects.create(created_user=self.user,
                                             with_user=user_2,
                                             status=Status.ACCEPTED)

        self.assertEqual(conn.activity_count, 1)
        self.assertEqual(conn.status, Status.ACCEPTED)
        self.assertEqual(conn.created_user, self.user)

        users = conn.users
        self.assertEqual(len(users), 2)
        self.assertTrue(self.user in users)
        self.assertTrue(user_2 in users)

    def test_get_or_create(self):
        """Test get or create object manager method."""
        user_2 = User.objects.create()

        conn, is_created = UserConnection.objects.get_or_create(
            created_user=self.user,
            with_user=user_2)
        self.assertTrue(is_created)

        conn_3, is_created = UserConnection.objects.get_or_create(
            created_user=self.user,
            with_user=user_2)
        self.assertFalse(is_created)
        self.assertEqual(conn, conn_3)

    def test_get_for_users(self):
        """Test getting connection between two users."""
        user_2 = create_user()

        conn = UserConnection.objects.create(created_user=self.user,
                                             with_user=user_2)

        conn_db = UserConnection.objects.get_for_users(user_1=self.user,
                                                       user_2=user_2)
        self.assertEqual(conn, conn_db)

        conn_db_2 = UserConnection.objects.get_for_users(user_1=user_2,
                                                         user_2=self.user)

        self.assertEqual(conn, conn_db_2)
