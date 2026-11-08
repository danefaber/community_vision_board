
from io import BytesIO
from unittest.mock import patch
from urllib.error import URLError

from django.test import SimpleTestCase, override_settings

from .spam_protection import verify_recaptcha


@override_settings(RECAPTCHA_SECRET_KEY="test-secret")
class RecaptchaTests(SimpleTestCase):

    @patch("board.spam_protection.urlopen")
    def test_missing_response(self, mock_urlopen):
        self.assertFalse(verify_recaptcha(""))
        mock_urlopen.assert_not_called()

    @patch("board.spam_protection.urlopen")
    def test_missing_secret(self, mock_urlopen):
        with override_settings(RECAPTCHA_SECRET_KEY=""):
            self.assertFalse(verify_recaptcha("test-token"))

        mock_urlopen.assert_not_called()

    @patch("board.spam_protection.urlopen")
    def test_successful_verification(self, mock_urlopen):
        mock_urlopen.return_value.__enter__.return_value = (
            BytesIO(b'{"success": true}')
        )

        self.assertTrue(verify_recaptcha("test-token"))

        request = mock_urlopen.call_args.args[0]
        self.assertEqual(request.get_method(), "POST")

    @patch("board.spam_protection.urlopen")
    def test_failed_verification(self, mock_urlopen):
        mock_urlopen.return_value.__enter__.return_value = (
            BytesIO(b'{"success": false}')
        )

        self.assertFalse(verify_recaptcha("invalid-token"))

    @patch("board.spam_protection.urlopen")
    def test_network_error(self, mock_urlopen):
        mock_urlopen.side_effect = URLError("Connection failed")

        self.assertFalse(verify_recaptcha("test-token"))

    @patch("board.spam_protection.urlopen")
    def test_invalid_google_response(self, mock_urlopen):
        mock_urlopen.return_value.__enter__.return_value = (
            BytesIO(b"invalid JSON")
        )

        self.assertFalse(verify_recaptcha("test-token"))

    @patch("board.spam_protection.urlopen")
    def test_timeout(self, mock_urlopen):
        mock_urlopen.side_effect = TimeoutError()

        self.assertFalse(verify_recaptcha("test-token"))
