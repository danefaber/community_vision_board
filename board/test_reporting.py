
from django.test import TestCase
from django.urls import reverse

from .models import Category, Post, PostReport


class PostReportingTests(TestCase):

    def setUp(self):
        self.category = Category.objects.create(
            name="T11 Test Category"
        )

        self.post = Post.objects.create(
            title="T11 Automated Test Post",
            description="Testing the reporting system.",
            category=self.category,
            contact_email="test@example.com",
            status="approved",
        )

    def test_report_approved_post(self):
        url = reverse("report_post", args=[self.post.pk])

        response = self.client.post(
            url,
            {
                "reason": "Spam",
                "details": "Automated test report",
            },
            HTTP_HOST="127.0.0.1",
        )

        self.assertEqual(response.status_code, 302)

        report = PostReport.objects.get(post=self.post)

        self.assertEqual(report.reason, "Spam")
        self.assertEqual(report.status, "pending")

        self.post.refresh_from_db()
        self.assertEqual(self.post.status, "approved")

    def test_cannot_report_unapproved_posts(self):
        url = reverse("report_post", args=[self.post.pk])

        for status in ("pending", "rejected"):
            self.post.status = status
            self.post.save(update_fields=["status"])

            response = self.client.post(
                url,
                {"reason": "Spam"},
                HTTP_HOST="127.0.0.1",
            )

            self.assertEqual(response.status_code, 404)

        self.assertEqual(PostReport.objects.count(), 0)
