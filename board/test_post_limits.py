
from datetime import timedelta

from django.test import RequestFactory, TestCase
from django.utils import timezone

from .models import Category, Post, PostSubmissionRecord
from .post_limits import (
    POSTS_PER_HOUR,
    PostRateLimitExceeded,
    create_post_with_rate_limit,
    get_ip_hash,
)


class PostLimitTests(TestCase):

    def setUp(self):
        self.factory = RequestFactory()

        self.category = Category.objects.create(
            name="Test Category"
        )

    def make_request(self, ip="192.0.2.1"):
        return self.factory.post(
            "/submit/",
            REMOTE_ADDR=ip,
        )

    def save_post(self):
        return Post.objects.create(
            title="Posting Limit Test",
            description="Temporary test post.",
            category=self.category,
            contact_email="test@example.com",
        )

    def test_five_allowed_sixth_blocked(self):
        request = self.make_request()

        for _ in range(POSTS_PER_HOUR):
            create_post_with_rate_limit(
                request,
                self.save_post,
            )

        self.assertEqual(
            Post.objects.count(),
            POSTS_PER_HOUR,
        )

        with self.assertRaises(PostRateLimitExceeded):
            create_post_with_rate_limit(
                request,
                self.save_post,
            )

        self.assertEqual(
            Post.objects.count(),
            POSTS_PER_HOUR,
        )

        self.assertEqual(
            PostSubmissionRecord.objects.count(),
            POSTS_PER_HOUR,
        )

    def test_different_ips_have_separate_limits(self):
        first_request = self.make_request("192.0.2.1")
        second_request = self.make_request("192.0.2.2")

        for _ in range(POSTS_PER_HOUR):
            create_post_with_rate_limit(
                first_request,
                self.save_post,
            )

        new_post = create_post_with_rate_limit(
            second_request,
            self.save_post,
        )

        self.assertIsNotNone(new_post.pk)
        self.assertEqual(
            Post.objects.count(),
            POSTS_PER_HOUR + 1,
        )

    def test_expired_submissions_do_not_count(self):
        request = self.make_request()

        for _ in range(POSTS_PER_HOUR):
            create_post_with_rate_limit(
                request,
                self.save_post,
            )

        oldest = PostSubmissionRecord.objects.first()

        PostSubmissionRecord.objects.filter(
            pk=oldest.pk,
        ).update(
            created_at=timezone.now() - timedelta(hours=2)
        )

        new_post = create_post_with_rate_limit(
            request,
            self.save_post,
        )

        self.assertIsNotNone(new_post.pk)
        self.assertEqual(
            Post.objects.count(),
            POSTS_PER_HOUR + 1,
        )

    def test_failed_submission_is_not_counted(self):
        request = self.make_request()

        def failing_save():
            self.save_post()
            raise ValueError("Simulated save failure")

        with self.assertRaises(ValueError):
            create_post_with_rate_limit(
                request,
                failing_save,
            )

        self.assertEqual(Post.objects.count(), 0)
        self.assertEqual(
            PostSubmissionRecord.objects.count(),
            0,
        )

    def test_ip_addresses_are_hashed(self):
        request = self.make_request("192.0.2.1")

        ip_hash = get_ip_hash(request)

        self.assertNotEqual(ip_hash, "192.0.2.1")
        self.assertEqual(len(ip_hash), 64)

        create_post_with_rate_limit(
            request,
            self.save_post,
        )

        record = PostSubmissionRecord.objects.first()

        self.assertEqual(record.ip_hash, ip_hash)
