from django.core import mail
from django.test import TestCase
from django.urls import reverse

from .models import Category, Post, Subscriber


class SubscribeTests(TestCase):
    def test_page_loads(self):
        response = self.client.get(reverse("board:subscribe"))
        self.assertEqual(response.status_code, 200)

    def test_new_email_is_subscribed(self):
        response = self.client.post(
            reverse("board:subscribe"), {"email": "Resident@Example.com"}
        )
        self.assertRedirects(response, reverse("board:subscribed"))
        subscriber = Subscriber.objects.get()
        self.assertEqual(subscriber.email, "resident@example.com")
        self.assertTrue(subscriber.active)

    def test_subscribing_twice_does_not_duplicate(self):
        self.client.post(reverse("board:subscribe"), {"email": "a@example.com"})
        response = self.client.post(
            reverse("board:subscribe"), {"email": "a@example.com"}
        )
        self.assertRedirects(response, reverse("board:subscribed"))
        self.assertEqual(Subscriber.objects.count(), 1)

    def test_inactive_subscriber_is_reactivated(self):
        Subscriber.objects.create(email="b@example.com", active=False)
        self.client.post(reverse("board:subscribe"), {"email": "b@example.com"})
        self.assertTrue(Subscriber.objects.get(email="b@example.com").active)

    def test_invalid_email_shows_error(self):
        response = self.client.post(
            reverse("board:subscribe"), {"email": "not-an-email"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Subscriber.objects.count(), 0)

    def test_new_subscriber_gets_approval_emails(self):
        self.client.post(reverse("board:subscribe"), {"email": "c@example.com"})
        post = Post.objects.create(
            title="Lost Cat",
            description="Gray tabby.",
            category=Category.objects.create(name="Lost Pets"),
            contact_email="owner@example.com",
        )
        post.status = "approved"
        post.save()
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("c@example.com", mail.outbox[0].bcc)