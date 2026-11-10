from django.core import mail
from django.core.management import call_command
from django.test import TestCase

from .models import Category, Event, Post, PostReport, Subscriber, VolunteerSignup


class DemoDataFixtureTests(TestCase):
    """Makes sure board/fixtures/demo_data.json still loads after model changes."""

    def test_demo_data_loads(self):
        call_command("loaddata", "demo_data", verbosity=0)
        self.assertEqual(Category.objects.count(), 4)
        self.assertEqual(Post.objects.count(), 12)
        self.assertEqual(Post.objects.filter(status="approved").count(), 8)
        self.assertEqual(Post.objects.filter(status="pending").count(), 3)
        self.assertEqual(Event.objects.count(), 6)
        self.assertEqual(VolunteerSignup.objects.count(), 3)
        self.assertEqual(PostReport.objects.count(), 2)
        self.assertEqual(Subscriber.objects.filter(active=True).count(), 2)

    def test_loading_demo_data_sends_no_emails(self):
        # A subscriber already exists, so approved posts in the fixture
        # would trigger emails if the signal didn't skip fixture loads.
        Subscriber.objects.create(email="existing@example.com")
        call_command("loaddata", "demo_data", verbosity=0)
        self.assertEqual(len(mail.outbox), 0)

    def test_demo_data_can_load_twice(self):
        call_command("loaddata", "demo_data", verbosity=0)
        call_command("loaddata", "demo_data", verbosity=0)
        self.assertEqual(Post.objects.count(), 12)