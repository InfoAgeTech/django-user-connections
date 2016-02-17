
class Status():
    """The different status's a user connection can be in.

    :field ACCEPTED: an accepted and current user connection
    :field DECLINED: a declined user connection.  This connection was never in
        an ACCEPTED state, or active.
    :field PENDING: the user connection is pending and waiting on a response
        from the user.
    :field INACTIVE: represents a user connection for two users that was once
        accepted and is no longer.
    """
    ACCEPTED = 'ACCEPTED'
    DECLINED = 'DECLINED'
    PENDING = 'PENDING'
    INACTIVE = 'INACTIVE'
    CHOICES = (
        (ACCEPTED, 'Accepted'),
        (DECLINED, 'Declined'),
        (PENDING, 'Pending'),
        (INACTIVE, 'Inactive')
    )
