# -*- coding: utf-8 -*-
import uuid

from django.contrib.auth import get_user_model
from django.test.testcases import TestCase
from django_user_connections.constants import Status
from django_user_connections.models import Connection

User = get_user_model()
random_string = lambda len = None: uuid.uuid4().hex[:len or 10]


def create_user(username=None, email=None):

    if not username:
        username = random_string()

    if not email:
        email = '{0}@{1}.com'.format(random_string(), random_string())

    return User.objects.create_user(username=username,
                                    email=email)


class BaseConnectionTestCase(TestCase):

    @classmethod
    def setUpClass(cls):
        super(BaseConnectionTestCase, cls).setUpClass()
        cls.usr = create_user()


class ConnectionManagerTests(BaseConnectionTestCase):


    def test_create_connection(self):
        """Test for adding a connection between 2 users."""
        usr_2 = User.objects.create()

        conn = Connection.objects.create(created_user=self.usr,
                                         with_user=usr_2,
                                         status=Status.PENDING)

        self.assertEqual(conn.activity_count, 1)
        self.assertEqual(conn.status, Status.PENDING)
        self.assertEqual(conn.created, self.usr)

        users = list(conn.users.all())
        self.assertEqual(len(users), 2)
        self.assertTrue(self.usr in users)
        self.assertTrue(usr_2 in users)

    def test_get_or_create(self):
        """Test get or create object manager method."""
        usr_2 = User.objects.create()

        conn, is_created = Connection.objects.get_or_create(created_user=self.usr,
                                                            with_user=usr_2)
        self.assertTrue(is_created)

        conn_3, is_created = Connection.objects.get_or_create(created_user=self.usr,
                                                              with_user=usr_2)
        self.assertFalse(is_created)
        self.assertEqual(conn, conn_3)


    def test_get_for_users(self):
        """Test getting connection between two users."""
        usr_2 = User.objects.create()

        conn = Connection.objects.create(created_user=self.usr,
                                         with_user=usr_2)

        conn_db = Connection.objects.get_for_users(user_id_1=self.usr.id,
                                                   user_id_2=usr_2.id)
        self.assertEqual(conn, conn_db)

        conn_db_2 = Connection.objects.get_for_users(user_id_1=usr_2.id,
                                                     user_id_2=self.usr.id)

        self.assertEqual(conn, conn_db_2)


class ConnectionTests(BaseConnectionTestCase):


    def test_accept_connection(self):
        """Test for accepting a connection."""
        usr_2 = create_user()

        conn = Connection.objects.create(created_user=self.usr,
                                         with_user=usr_2,
                                         status=Status.PENDING)

        self.assertEqual(conn.status, Status.PENDING)
        conn.accept()
        self.assertEqual(conn.status, Status.ACCEPTED)

    def test_decline_connection(self):
        """Test for declining a connection."""
        usr_2 = create_user()

        conn = Connection.objects.create(created_user=self.usr,
                              with_user=usr_2,
                              status=Status.PENDING)

        self.assertEqual(conn.status, Status.PENDING)
        conn.decline()
        self.assertEqual(conn.status, Status.DECLINED)

    def test_incremement_activity_count(self):
        """Test for incrementing the total activity count for a connection."""
        usr_2 = create_user()

        conn = Connection.objects.create(created_user=self.usr,
                              with_user=usr_2)

        self.assertEqual(conn.activity_count, 1)
        conn.increment_activity_count()

        conn = Connection.objects.get(id=conn.id)
        self.assertEqual(conn.activity_count, 2)

    def test_incremement_activity_count_by_users(self):
        """Test for incrementing the total activity count for a connection."""
        usr_2 = create_user()

        conn = Connection.objects.create(created_user=self.usr,
                                         with_user=usr_2)

        self.assertEqual(conn.activity_count, 1)
        Connection.increment_activity_count_by_users(user_id_1=self.usr.id,
                                                     user_id_2=usr_2.id)

        conn = Connection.objects.get(id=conn.id)
        self.assertEqual(conn.activity_count, 2)

    def test_get_by_user_id(self):
        """Test for getting connections by a specific user id."""
        usr_2 = create_user()
        users = [create_user() for i in range(10)]

        for user in users:
            conn = Connection.objects.create(created_user=usr_2,
                                             with_user=user)

        connections = Connection.objects.get_by_user_id(user_id=usr_2.id)
        self.assertEqual(len(connections), 10)

    def test_get_connection_by_user_ids(self):
        """Test for getting a connection between 2 users."""
        usr_2 = create_user()

        conn = Connection.objects.create(created_user=self.usr,
                              with_user=usr_2,
                              status=Status.PENDING)

        conn_1 = Connection.objects.get_for_users(user_id_1=self.usr.id, user_id_2=usr_2.id)
        self.assertEqual(conn, conn_1)
        conn_2 = Connection.objects.get_for_users(user_id_1=usr_2.id, user_id_2=self.usr.id)
        self.assertEqual(conn, conn_2)

    def test_get_for_user_id(self):
        """Test for retrieving the id of the user the connection is intended for.
        """
        usr_2 = create_user()

        conn = Connection.objects.create(created_user=self.usr,
                              with_user=usr_2,
                              status=Status.PENDING)

        self.assertEqual(conn.get_for_user_id(), usr_2.id)


    def test_get_by_token(self):
        """Test for getting a connection by a token."""
        usr_2 = create_user()

        conn = Connection.objects.create(created_user=self.usr,
                                         with_user=usr_2,
                                         status=Status.PENDING)

        conn_2 = Connection.objects.get_by_token(token=conn.token)

        self.assertEqual(conn, conn_2)

    def test_get_next_token(self):
        """Test for getting the next token."""
        token = Connection.objects.get_next_token(length=20)
        self.assertEqual(len(token), 20)
