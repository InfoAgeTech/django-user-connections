# -*- coding: utf-8 -*-

from django.contrib.auth import get_user_model
from django.http.response import Http404
from django.shortcuts import redirect
from django_user_connections import get_user_connection_model

from ..constants import Status


User = get_user_model()
UserConnection = get_user_connection_model()


class UserConnectionViewMixin(object):
    """Gets a user connection by the user connection_id from the url.  The
    user connection can be retrieved in one of three ways via url args.

    1) <connection_id> - this can be one of two things:
        1) the actual id of the user connection.  This is assumed to be a digit
           value.
        2) username. The connection id can also be a username since a username
           must include at least one character value and will not be all
           digits.
    2) <connection_token> = this is the token for the user connection.

    This view mixin places the following attributes on the view:

    * connection_id_pk_url_kwarg: the url primary key for the connection.
        Defaults to 'connection_id'.  This value assumes that if you're using
        an all digit value that it's referring to a connection id.  If the
        value is not a digit, it will try to get the connection by username.
    * user_connection: the UserConnection object for the users connected.
    * connection_user: the user the authenticated user is connected with.
    """
    pk_url_kwarg = 'connection_id'
    connection_id_pk_url_kwarg = 'connection_id'
    user_connection = None
    connection_user = None
    model = UserConnection
    context_object_name = 'user_connection'

    def dispatch(self, *args, **kwargs):
        connection_key = kwargs.get(self.connection_id_pk_url_kwarg)

        if 'connection_token' in kwargs:
            # Attempting to get the user connection by the connection token.
            self.user_connection = UserConnection.objects.get_by_token_or_404(
                                        token=kwargs.get('connection_token'))
        elif connection_key.isdigit():
            # It's the connection primary key object (integer).
            self.user_connection = UserConnection.objects.get_by_id_or_404(
                                id=kwargs.get(self.connection_id_pk_url_kwarg),
                                prefetch_related=('with_user',))

        else:
            # The connection key is a username (string)
            if self.request.user.username == connection_key:
                return redirect('/')

            try:
                connection_user = User.objects.get(username=connection_key)
            except:
                raise Http404

            self.user_connection = UserConnection.objects.get_for_users(
                            user_1=self.request.user,
                            user_2=connection_user)

            if not self.user_connection:
                raise Http404

        if self.request.user.id not in self.user_connection.user_ids:
            # This connection doesn't belong to the authenticated user
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


class UserConnectionSingleObjectViewMixin(UserConnectionViewMixin):

    def get_object(self):
        self.user_connection


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
    """View mixin for getting the authenticated user's connections.

    * user_connections_accepted: queryset of accepted user connections
    * user_connections_declined: queryset of declined user connections
    * user_connections_pending: queryset of pending user connections
    * user_connections_inactivated: queryset of inactivated user connections
    * connection_user_ids: a list of user ids the authenticated user is
        connected with.
    """
    user_connections_accepted = None
    user_connections_declined = None
    user_connections_pending = None
    user_connections_inactivated = None
    connection_user_ids = None

    def dispatch(self, *args, **kwargs):
        """Puts the querysets by type on the view.  The benefit to this the
        query only runs when you want that type of user connection status. So
        if no pending connection are wanted, no queries are run for that type.
        """
        self.user_connections = self.get_user_connections()
        self.user_connections_accepted = self.user_connections.filter(
                                                        status=Status.ACCEPTED)
        self.user_connections_declined = self.user_connections.filter(
                                                        status=Status.DECLINED)
        self.user_connections_pending = self.user_connections.filter(
                                                        status=Status.PENDING)
        self.user_connections_inactivated = self.user_connections.filter(
                                                        status=Status.INACTIVE)
        self.connection_user_ids = UserConnection.objects.get_user_ids(
                                                user_id=self.request.user.id)
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
        context['user_connections_inactivated'] = self.user_connections_inactivated
        context['connection_user_ids'] = self.connection_user_ids
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
