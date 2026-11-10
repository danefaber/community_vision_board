
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
    list_filter = ("status", "category")
    search_fields = ("title", "description", "location")
    ordering = ("created_at",)
    readonly_fields = ("created_at",)
    actions = ("approve_posts", "reject_posts")

    @admin.action(description="Approve selected pending posts")
    def approve_posts(self, request, queryset):
        posts = queryset.filter(status="pending")
        count = 0

        for post in posts:
            post.status = "approved"
            post.save(update_fields=["status"])
            self.log_change(request, post, "Approved pending post.")
            count += 1
        if count:
            self.message_user(
                request,
                f"{count} pending post(s) approved.",
                level="success",
            )
        else:
            self.message_user(
                request,
                "No posts changed. Only posts marked Pending Review can be approved.",
                level="warning",
            )

    @admin.action(description="Reject selected pending posts")
    def reject_posts(self, request, queryset):
        posts = queryset.filter(status="pending")
        count = 0

        for post in posts:
            post.status = "rejected"
            post.save(update_fields=["status"])
            self.log_change(request, post, "Rejected pending post.")
            count += 1

        if count:
            self.message_user(
                request,
                f"{count} pending post(s) rejected.",
                level="success",
            )
        else:
            self.message_user(
                request,
                "No posts changed. Only posts marked Pending Review can be rejected.",
                level="warning",
            )

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
