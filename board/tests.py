from django.test import TestCase
from django.core import mail

from .models import Category, Post, Subscriber

# Create your tests here.

class ApprovalNotificationTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Volunteering")
        Subscriber.objects.create(email="active@example.com")
        Subscriber.objects.create(email="inactive@example.com", active=False)

    def make_post(self, **kwargs):
        return Post.objects.create(
            title="Park cleanup",
            description="Help clean up the city park.",
            category=self.category,
            contact_email="organizer@example.com",
            **kwargs,
        )

    def test_new_post_is_pending_and_sends_no_email(self):
        post = self.make_post()
        self.assertEqual(post.status, "pending")
        self.assertEqual(len(mail.outbox), 0)

    def test_approving_a_post_emails_active_subscribers(self):
        post = self.make_post()
        post.status = "approved"
        post.save()
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("Park cleanup", mail.outbox[0].subject)
        self.assertEqual(mail.outbox[0].bcc, ["active@example.com"])

    def test_inactive_subscribers_are_not_emailed(self):
        post = self.make_post()
        post.status = "approved"
        post.save()
        self.assertNotIn("inactive@example.com", mail.outbox[0].bcc)

    def test_saving_an_approved_post_again_does_not_resend(self):
        post = self.make_post()
        post.status = "approved"
        post.save()
        post.title = "Park cleanup (updated)"
        post.save()
        self.assertEqual(len(mail.outbox), 1)

    def test_rejecting_a_post_sends_no_email(self):
        post = self.make_post()
        post.status = "rejected"
        post.save()
        self.assertEqual(len(mail.outbox), 0)

    def test_no_email_when_there_are_no_subscribers(self):
        Subscriber.objects.all().delete()
        post = self.make_post()
        post.status = "approved"
        post.save()
        self.assertEqual(len(mail.outbox), 0)
