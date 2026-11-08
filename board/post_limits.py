
from datetime import timedelta

from django.db import transaction
from django.utils import timezone
from django.utils.crypto import salted_hmac

from .models import PostSubmissionLock, PostSubmissionRecord


POSTS_PER_HOUR = 5


class PostRateLimitExceeded(Exception):
    pass


def get_ip_hash(request):
    # Use the IP provided by Django's server environment.
    # Do not trust a user-supplied forwarding header.
    ip_address = request.META.get("REMOTE_ADDR")

    if not ip_address:
        raise ValueError("Client IP address is unavailable.")

    return salted_hmac(
        "board.post_limits",
        ip_address,
        algorithm="sha256",
    ).hexdigest()


def create_post_with_rate_limit(request, create_post):
    ip_hash = get_ip_hash(request)

    # Ensure each IP has a row we can lock.
    lock, _ = PostSubmissionLock.objects.get_or_create(
        ip_hash=ip_hash,
    )

    with transaction.atomic():
        # Serialize submissions from the same IP on MySQL.
        PostSubmissionLock.objects.select_for_update().get(
            pk=lock.pk,
        )

        cutoff = timezone.now() - timedelta(hours=1)

        recent_count = PostSubmissionRecord.objects.filter(
            ip_hash=ip_hash,
            created_at__gte=cutoff,
        ).count()

        if recent_count >= POSTS_PER_HOUR:
            raise PostRateLimitExceeded(
                "You have reached the limit of 5 posts per hour."
            )

        # The caller supplies the function that saves the new post.
        post = create_post()

        if post is None or post.pk is None:
            raise ValueError("The post was not saved.")

        # Record only a successfully saved post.
        PostSubmissionRecord.objects.create(
            ip_hash=ip_hash,
        )

        return post
