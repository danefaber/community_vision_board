from django.conf import settings
from django.core.mail import send_mail
from django.urls import reverse


def build_edit_url(request, post):
    """Full URL to the post's private edit page."""
    return request.build_absolute_uri(
        reverse("board:edit_post", args=[post.edit_token])
    )


def send_edit_link(request, post):
    """
    Email the poster their private edit link.

    Call this right after submit_post() succeeds.
    Returns True if the email was sent, False if sending failed.
    """
    edit_url = build_edit_url(request, post)

    body = (
        f"Thanks for posting \"{post.title}\" on the Community Vision Board.\n\n"
        "Your post is waiting for a moderator to review it. "
        "Most posts are reviewed within 1-2 days.\n\n"
        "Use this private link to edit your post later:\n"
        f"{edit_url}\n\n"
        "Keep this link to yourself. Anyone who has it can edit your post. "
        "Edited posts go back to moderator review before they're shown again.\n"
    )

    try:
        sent = send_mail(
            subject=f"Your edit link for \"{post.title}\"",
            message=body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[post.contact_email],
        )
    except Exception:
        return False

    return sent == 1