# -*- coding: utf-8 -*-

from ..constants import Status
from ..models import UserConnection
from django.contrib.auth import get_user_model
from django.http.response import Http404

User = get_user_model()


class UserConnectionViewMixin(object):
    """Gets a user connection by the user connection_id from the url.

    This view mixin places the following attributes on the view:

    * connection_id_pk_url_kwarg: the url primary key for the connection.
        Defaults to 'connection_id'
    * user_connection: the UserConnection object for the users connected.
    * connection_user: the user the authenticated user is connected with.
    """
    connection_id_pk_url_kwarg = 'connection_id'
    user_connection = None
    connection_user = None

    def dispatch(self, *args, **kwargs):
        # TODO: if I want to be able to hit a connection by their username,
        #       i can do a check on the connection_id to see if it's digits
        #       (which would represent a connection_id) or at least 1 non-digit
        #       (which would represent a username)
        connection_key = kwargs.get(self.connection_id_pk_url_kwarg)

        if connection_key.isdigit():
            # It's the connection primary key object.
            self.user_connection = UserConnection.objects.get_by_id_or_404(
                                id=kwargs.get(self.connection_id_pk_url_kwarg),
                                prefetch_related=('with_user',))

        else:
            # The connection key is a username (string)
            try:
                connection_user = User.objects.get(username=connection_key)
            except:
                raise Http404

            self.user_connection = UserConnection.objects.get_for_users(
                            user_1=self.request.user,
                            user_2=connection_user)

            if not self.user_connection:
                raise Http404

        self.connection_user = self.user_connection.get_connected_user(
                                                        user=self.request.user)
        return super(UserConnectionViewMixin, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(UserConnectionViewMixin, self).get_context_data(
                                                                    **kwargs)
        context['user_connection'] = self.user_connection
        context['connection_user'] = self.connection_user
        return context


class BaseUserConnectionsViewMixin(object):
    """Base user connection mixin."""
    user_connections = None

    def get_user_connections(self, **kwargs):
        if self.user_connections:
            return self.user_connections

        return (UserConnection.objects.get_by_user(user=self.request.user,
                                                   **kwargs)
                              .order_by('-activity_count')
                              .prefetch_related('created_user',
                                                'with_user'))


class UserConnectionsViewMixin(BaseUserConnectionsViewMixin):
    """View mixin for getting the authenticated user's connections."""
    user_connections_accepted = None
    user_connections_declined = None
    user_connections_pending = None

    def dispatch(self, *args, **kwargs):
        self.user_connections = self.get_user_connections()
        self.user_connections_accepted = self.user_connections.filter(
                                                        status=Status.ACCEPTED)
        self.user_connections_declined = self.user_connections.filter(
                                                        status=Status.DECLINED)
        self.user_connections_pending = self.user_connections.filter(
                                                        status=Status.PENDING)
        return super(UserConnectionsViewMixin, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(UserConnectionsViewMixin, self).get_context_data(
                                                                    **kwargs)
        context['user_connections'] = self.user_connections
        # I could also create lambda functions here that just sorts through
        # the user_connections to get the correct status'.  The problem with
        # that is I can't filter the query further by leveraging a queryset.
        context['user_connections_accepted'] = self.user_connections_accepted
        context['user_connections_declined'] = self.user_connections_declined
        context['user_connections_pending'] = self.user_connections_pending
        return context


class UserConnectionsByUserViewMixin(UserConnectionsViewMixin):
    """View mixin for getting the authenticated user's connections and orders
    them by activity count and returns a tuple of the user connected with along
    with the connection.
    """
    user_connections_by_user = None
    connections_page_size = 25

    def dispatch(self, *args, **kwargs):
        self.user_connections_by_user = {
            conn.get_connected_user(self.request.user).id: conn
            for conn in self.get_user_connections(status=Status.ACCEPTED)[:100]
        }
        return super(UserConnectionsByUserViewMixin, self).dispatch(*args,
                                                                    **kwargs)

    def get_context_data(self, **kwargs):
        """
        :param page_size: the number of connections to return
        :return: tuple with the connected user being the first part, the second
            part being the UserConnection object.
        """
        context = super(UserConnectionsByUserViewMixin, self).get_context_data(
                                                                    **kwargs)
        context['user_connections_by_user'] = self.user_connections_by_user
        return context
