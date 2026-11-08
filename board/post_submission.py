
from .post_limits import create_post_with_rate_limit
from .spam_protection import verify_recaptcha


class CaptchaVerificationFailed(Exception):
    pass


def submit_post(request, save_post):
    captcha_response = request.POST.get(
        "g-recaptcha-response", ""
    )

    if not verify_recaptcha(captcha_response):
        raise CaptchaVerificationFailed(
            "Please complete the CAPTCHA verification."
        )

    def save_pending_post():
        post = save_post()
        if post is not None and post.pk is not None:
            if post.status != "pending":
                post.status = "pending"
                post.save(update_fields=["status"])
        return post

    return create_post_with_rate_limit(
        request,
        save_pending_post,
    )
