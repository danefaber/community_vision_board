
from django.contrib import admin
from .models import (
    Category,
    Post,
    Event,
    VolunteerSignup,
    PostReport,
    Subscriber,
)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "status", "created_at")
    list_filter = ("category", "status")
    search_fields = ("title", "description", "location")
    list_editable = ("status",)


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ("post", "start_time", "end_time")


@admin.register(VolunteerSignup)
class VolunteerSignupAdmin(admin.ModelAdmin):
    list_display = ("name", "post", "email", "created_at")


@admin.register(PostReport)
class PostReportAdmin(admin.ModelAdmin):
    list_display = ("post", "reason", "status", "created_at")
    list_filter = ("status",)


@admin.register(Subscriber)
class SubscriberAdmin(admin.ModelAdmin):
    list_display = ("email", "active", "created_at")
    list_filter = ("active",)
