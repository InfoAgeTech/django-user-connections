from __future__ import unicode_literals

from django.db import models


class AbstractUserConnectionMixin(models.Model):
    """The abstract model to add functionality to the model.
    """

    class Meta:
        abstract = True

    def my_test_method(self):
        return 'worked'
