from unittest.mock import patch

from django.core import mail
from django.core.exceptions import ValidationError
from django.test import RequestFactory, TestCase

from .edit_links import build_edit_url, send_edit_link
from .models import Category, Post


class EditLinkEmailTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Lost Pets")
        self.post = Post.objects.create(
            title="Lost Dog",
            description="Brown lab, answers to Max.",
            category=self.category,
            contact_email="owner@example.com",
        )
        self.request = RequestFactory().get("/")

    def test_sends_one_email_to_poster(self):
        self.assertTrue(send_edit_link(self.request, self.post))
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ["owner@example.com"])

    def test_email_contains_full_edit_link(self):
        send_edit_link(self.request, self.post)
        expected = f"http://testserver/posts/edit/{self.post.edit_token}/"
        self.assertIn(expected, mail.outbox[0].body)
        self.assertEqual(build_edit_url(self.request, self.post), expected)

    def test_edit_link_opens_edit_page(self):
        url = build_edit_url(self.request, self.post)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_returns_false_when_sending_fails(self):
        with patch("board.edit_links.send_mail", side_effect=OSError):
            self.assertFalse(send_edit_link(self.request, self.post))


class PostFieldTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Help Wanted")

    def make_post(self, **kwargs):
        fields = {
            "title": "Snow shoveling",
            "description": "Need help after storms.",
            "category": self.category,
            "contact_email": "poster@example.com",
        }
        fields.update(kwargs)
        return Post(**fields)

    def test_defaults(self):
        post = self.make_post()
        post.save()
        self.assertEqual(post.contact_method, "email")
        self.assertFalse(post.is_resolved)
        self.assertIsNone(post.resolved_at)

    def test_phone_method_requires_phone_number(self):
        post = self.make_post(contact_method="phone")
        with self.assertRaises(ValidationError):
            post.full_clean()
        post.contact_phone = "402-555-0100"
        post.full_clean()

    def test_resolving_sets_and_clears_resolved_at(self):
        post = self.make_post()
        post.save()
        post.is_resolved = True
        post.save()
        self.assertIsNotNone(post.resolved_at)
        post.is_resolved = False
        post.save()
        self.assertIsNone(post.resolved_at)

    def test_resolving_with_update_fields_saves_resolved_at(self):
        post = self.make_post()
        post.save()
        post.is_resolved = True
        post.save(update_fields=["is_resolved"])
        post.refresh_from_db()
        self.assertIsNotNone(post.resolved_at)

    def test_category_plural_name(self):
        self.assertEqual(Category._meta.verbose_name_plural, "categories")