
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.test import TestCase
from django.urls import reverse

from .models import Category, Post, PostReport


class ModeratorReportingTests(TestCase):

    def setUp(self):
        self.category = Category.objects.create(
            name="T11 Moderator Test"
        )

        self.post = Post.objects.create(
            title="Moderator Test Post",
            description="Testing report moderation.",
            category=self.category,
            contact_email="test@example.com",
            status="approved",
        )

        self.report = PostReport.objects.create(
            post=self.post,
            reason="Spam",
            status="pending",
        )

        self.moderator = get_user_model().objects.create_user(
            username="test_moderator",
            password="temporary-test-password",
            is_staff=True,
        )

        self.moderator.groups.add(
            Group.objects.get(name="Moderators")
        )

        self.client.force_login(self.moderator)

        self.queue_url = reverse(
            "admin:board_postreport_changelist"
        )

    def action_data(self, action):
        return {
            "action": action,
            "_selected_action": [str(self.report.pk)],
            "select_across": "0",
        }

    def test_moderator_permissions(self):
        response = self.client.get(self.queue_url)
        self.assertEqual(response.status_code, 200)

        other_user = get_user_model().objects.create_user(
            username="unprivileged_staff",
            is_staff=True,
        )

        self.client.force_login(other_user)

        response = self.client.get(self.queue_url)
        self.assertEqual(response.status_code, 403)

    def test_dismiss_report(self):
        response = self.client.post(
            self.queue_url,
            self.action_data("dismiss_reports"),
        )

        self.assertEqual(response.status_code, 302)

        self.report.refresh_from_db()
        self.post.refresh_from_db()

        self.assertEqual(self.report.status, "dismissed")
        self.assertEqual(self.post.status, "approved")

    def test_hide_requires_confirmation(self):
        data = self.action_data("hide_reported_posts")

        response = self.client.post(self.queue_url, data)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response,
            "admin/board/postreport/confirm_hide.html",
        )

        self.report.refresh_from_db()
        self.post.refresh_from_db()

        self.assertEqual(self.report.status, "pending")
        self.assertEqual(self.post.status, "approved")

        data["confirm_hide"] = "yes"

        response = self.client.post(self.queue_url, data)

        self.assertEqual(response.status_code, 302)

        self.report.refresh_from_db()
        self.post.refresh_from_db()

        self.assertEqual(self.report.status, "reviewed")
        self.assertEqual(self.post.status, "rejected")

    def test_completed_reports_cannot_be_reprocessed(self):
        for status in ("dismissed", "reviewed"):
            self.report.status = status
            self.report.save(update_fields=["status"])

            action = (
                "dismiss_reports"
                if status == "dismissed"
                else "hide_reported_posts"
            )

            response = self.client.post(
                self.queue_url,
                self.action_data(action),
            )

            self.assertEqual(response.status_code, 302)

            self.report.refresh_from_db()
            self.post.refresh_from_db()

            self.assertEqual(self.report.status, status)
            self.assertEqual(self.post.status, "approved")
