# -*- coding: utf-8 -*-


class Status:
    ACCEPTED = 'accepted'
    DECLINED = 'declined'
    PENDING = 'pending'
    CHOICES = (
        (ACCEPTED, 'Accepted'),
        (DECLINED, 'Declined'),
        (PENDING, 'Pending'))
