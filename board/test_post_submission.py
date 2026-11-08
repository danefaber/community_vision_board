
from unittest.mock import patch

from django.test import RequestFactory, TestCase

from .models import Category, Post, PostSubmissionRecord
from .post_limits import PostRateLimitExceeded
from .post_submission import (
    CaptchaVerificationFailed,
    submit_post,
)


class PostSubmissionTests(TestCase):

    def setUp(self):
        self.factory = RequestFactory()

        self.category = Category.objects.create(
            name="Test Category"
        )

        self.request = self.factory.post(
            "/submit/",
            {"g-recaptcha-response": "test-token"},
            REMOTE_ADDR="192.0.2.1",
        )

    def save_post(self):
        return Post.objects.create(
            title="Submission Test",
            description="Testing protected post submission.",
            category=self.category,
            contact_email="test@example.com",
            status="approved",
        )

    @patch("board.post_submission.verify_recaptcha",
           return_value=True)
    def test_valid_submission(self, mock_verify):
        post = submit_post(
            self.request,
            self.save_post,
        )

        self.assertIsNotNone(post.pk)
        self.assertEqual(post.status, "pending")
        self.assertEqual(Post.objects.count(), 1)
        self.assertEqual(
            PostSubmissionRecord.objects.count(),
            1,
        )
        mock_verify.assert_called_once_with("test-token")

    @patch("board.post_submission.verify_recaptcha",
           return_value=False)
    def test_invalid_captcha(self, mock_verify):
        with self.assertRaises(CaptchaVerificationFailed):
            submit_post(
                self.request,
                self.save_post,
            )

        self.assertEqual(Post.objects.count(), 0)
        self.assertEqual(
            PostSubmissionRecord.objects.count(),
            0,
        )

    def test_missing_captcha(self):
        request = self.factory.post(
            "/submit/",
            {},
            REMOTE_ADDR="192.0.2.1",
        )

        with self.assertRaises(CaptchaVerificationFailed):
            submit_post(request, self.save_post)

        self.assertEqual(Post.objects.count(), 0)

    @patch("board.post_submission.verify_recaptcha",
           return_value=True)
    def test_rate_limit(self, mock_verify):
        for _ in range(5):
            submit_post(
                self.request,
                self.save_post,
            )

        with self.assertRaises(PostRateLimitExceeded):
            submit_post(
                self.request,
                self.save_post,
            )

        self.assertEqual(Post.objects.count(), 5)
        self.assertEqual(
            PostSubmissionRecord.objects.count(),
            5,
        )

    @patch("board.post_submission.verify_recaptcha",
           return_value=True)
    def test_failed_save_rolls_back(self, mock_verify):

        def failing_save():
            self.save_post()
            raise ValueError("Simulated failure")

        with self.assertRaises(ValueError):
            submit_post(
                self.request,
                failing_save,
            )

        self.assertEqual(Post.objects.count(), 0)
        self.assertEqual(
            PostSubmissionRecord.objects.count(),
            0,
        )
