from django.conf import settings
from django.core.mail import EmailMessage
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from .models import Post, Subscriber


@receiver(pre_save, sender=Post)
def remember_old_status(sender, instance, **kwargs):
    """Before a post is saved, remember what its status was so we can tell if it just got approved."""
    if instance.pk:
        old = Post.objects.filter(pk=instance.pk).values_list("status", flat=True).first()
        instance._old_status = old
    else:
        instance._old_status = None


@receiver(post_save, sender=Post)
def notify_subscribers_on_approval(sender, instance, created, **kwargs):
    """After a post is saved, email active subscribers if it was just approved."""
    if kwargs.get("raw"):
        return  # skip when loading fixtures
    
    just_approved = instance.status == "approved" and instance._old_status != "approved"
    if not just_approved:
        return

    emails = list(Subscriber.objects.filter(active=True).values_list("email", flat=True))
    if not emails:
        return

    body = (
        f"A new post was just added to the Community Vision Board.\n\n"
        f"{instance.title}\n"
        f"Category: {instance.category}\n"
    )
    if instance.location:
        body += f"Location: {instance.location}\n"
    body += f"\n{instance.description}\n"

    # BCC so subscribers can't see each other's email addresses
    EmailMessage(
        subject=f"New post: {instance.title}",
        body=body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[],
        bcc=emails,
    ).send(fail_silently=True)