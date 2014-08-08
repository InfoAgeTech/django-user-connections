from __future__ import unicode_literals

from django.db import models


class AbstractUserConnectionMixin(models.Model):
    """The abstract notification model to add functionality to the
    Notification's model.
    """

    class Meta:
        abstract = True

    def my_test_method(self):
        return 'worked'
