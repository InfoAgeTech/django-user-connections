## -*- coding: utf-8 -*-
#from django.contrib import admin
#from mongo_user_connections.models import Connection
#from bb_admin.base_admin import AbstractBaseAdmin
#
#
#class ConnectionAdmin(AbstractBaseAdmin):
#    list_filter = ('status',)
#    
#    def __init__(self, *args, **kwargs):
#        super(ConnectionAdmin, self).__init__(*args, **kwargs)
#        self.list_display += ('with_user', 'status', 'token')
#        self.search_fields += ('with_user__username',)
#        
#admin.site.register(Connection, ConnectionAdmin)