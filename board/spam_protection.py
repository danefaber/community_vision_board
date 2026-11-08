
import json

from urllib.error import URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from django.conf import settings


RECAPTCHA_VERIFY_URL = (
    "https://www.google.com/recaptcha/api/siteverify"
)


def verify_recaptcha(response_token):
    secret_key = getattr(
        settings,
        "RECAPTCHA_SECRET_KEY",
        "",
    )

    # Reject missing configuration or missing CAPTCHA responses.
    if not secret_key or not response_token:
        return False

    data = urlencode({
        "secret": secret_key,
        "response": response_token,
    }).encode("utf-8")

    request = Request(
        RECAPTCHA_VERIFY_URL,
        data=data,
        method="POST",
    )

    try:
        with urlopen(request, timeout=5) as response:
            result = json.load(response)

    except (URLError, TimeoutError, ValueError, OSError):
        return False

    return result.get("success") is True
