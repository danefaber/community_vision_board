
import uuid
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


class Category(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    
    class Meta:
        verbose_name_plural = "categories"

    def __str__(self):
        return self.name


class Post(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending Review"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
    ]
    
    CONTACT_METHOD_CHOICES = [
        ("email", "Email"),
        ("phone", "Phone"),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="posts",
    )

    location = models.CharField(max_length=255, blank=True)
    contact_name = models.CharField(max_length=100, blank=True)
    # Always required: private edit links are emailed here.
    contact_email = models.EmailField()
    # How the poster wants the public to reach them.
    contact_method = models.CharField(
        max_length=10,
        choices=CONTACT_METHOD_CHOICES,
        default="email",
    )
    contact_phone = models.CharField(max_length=20, blank=True)

    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default="pending",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    # Mark-as-resolved (found pet, filled job, finished event).
    is_resolved = models.BooleanField(default=False)
    resolved_at = models.DateTimeField(null=True, blank=True)

    edit_token = models.UUIDField(
       default=uuid.uuid4,
       unique=True,
       editable=False,
    )
    
    def clean(self):
        if self.contact_method == "phone" and not self.contact_phone:
            raise ValidationError(
                {"contact_phone": "Enter a phone number, or choose email as the contact method."}
            )

    def save(self, *args, **kwargs):
        # Keep resolved_at in sync with is_resolved.
        if self.is_resolved and self.resolved_at is None:
            self.resolved_at = timezone.now()
        elif not self.is_resolved:
            self.resolved_at = None
        update_fields = kwargs.get("update_fields")
        if update_fields is not None and "is_resolved" in update_fields:
            kwargs["update_fields"] = set(update_fields) | {"resolved_at"}
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.title


class Event(models.Model):
    post = models.OneToOneField(
        Post,
        on_delete=models.CASCADE,
        related_name="event",
    )
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.post.title} - {self.start_time}"


class VolunteerSignup(models.Model):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name="volunteer_signups",
    )
    name = models.CharField(max_length=100)
    email = models.EmailField()
    message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.post.title}"


class PostReport(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending Review"),
        ("reviewed", "Reviewed"),
        ("dismissed", "Dismissed"),
    ]

    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name="reports",
    )
    reason = models.CharField(max_length=100)
    details = models.TextField(blank=True)
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default="pending",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Report: {self.post.title}"


class Subscriber(models.Model):
    email = models.EmailField(unique=True)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email

class PostSubmissionRecord(models.Model):
    ip_hash = models.CharField(max_length=64)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["ip_hash", "created_at"]),
        ]

class PostSubmissionLock(models.Model):
    ip_hash = models.CharField(
        max_length=64,
        unique=True,
    )
