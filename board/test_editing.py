
import uuid

from django.test import Client, TestCase
from django.urls import reverse

from .models import Category, Post


class PrivatePostEditingTests(TestCase):

    def setUp(self):
        self.client = Client(HTTP_HOST="127.0.0.1")

        self.category = Category.objects.create(
            name="Test Category"
        )

        self.post = Post.objects.create(
            title="Original Title",
            description="Original description",
            category=self.category,
            contact_email="test@example.com",
            status="approved",
        )

        self.url = reverse(
            "edit_post",
            kwargs={"token": self.post.edit_token},
        )

    def form_data(self, **changes):
        data = {
            "title": self.post.title,
            "description": self.post.description,
            "category": self.category.pk,
            "location": self.post.location,
            "contact_name": self.post.contact_name,
            "contact_email": self.post.contact_email,
        }
        data.update(changes)
        return data

    def test_valid_edit_link(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Original Title")

    def test_invalid_edit_link(self):
        invalid_url = reverse(
            "edit_post",
            kwargs={"token": uuid.uuid4()},
        )

        response = self.client.get(invalid_url)

        self.assertEqual(response.status_code, 404)

    def test_viewing_does_not_change_status(self):
        self.client.get(self.url)

        self.post.refresh_from_db()

        self.assertEqual(self.post.status, "approved")

    def test_editing_requires_moderation(self):
        response = self.client.post(
            self.url,
            self.form_data(title="Updated Title"),
        )

        self.post.refresh_from_db()

        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.post.title, "Updated Title")
        self.assertEqual(self.post.status, "pending")

    def test_status_and_token_protected(self):
        original_token = self.post.edit_token

        response = self.client.post(
            self.url,
            self.form_data(
                title="Security Test",
                status="approved",
                edit_token=str(uuid.uuid4()),
            ),
        )

        self.post.refresh_from_db()

        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.post.status, "pending")
        self.assertEqual(self.post.edit_token, original_token)

    def test_no_changes_preserves_status(self):
        response = self.client.post(
            self.url,
            self.form_data(),
        )

        self.post.refresh_from_db()

        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.post.status, "approved")

    def test_invalid_form_preserves_post(self):
        response = self.client.post(
            self.url,
            self.form_data(title=""),
        )

        self.post.refresh_from_db()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.post.title, "Original Title")
        self.assertEqual(self.post.status, "approved")

    def test_old_link_rejected_after_rotation(self):
        old_url = self.url

        self.post.edit_token = uuid.uuid4()
        self.post.save(update_fields=["edit_token"])

        new_url = reverse(
            "edit_post",
            kwargs={"token": self.post.edit_token},
        )

        self.assertEqual(
            self.client.get(old_url).status_code,
            404,
        )
        self.assertEqual(
            self.client.get(new_url).status_code,
            200,
        )
