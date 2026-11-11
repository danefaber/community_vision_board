
from django.contrib import admin
from .models import (
    Category,
    Post,
    Event,
    VolunteerSignup,
    PostReport,
    Subscriber,
)
from django.template.response import TemplateResponse

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "status", "is_resolved", "created_at")
    list_filter = ("status", "is_resolved", "category")
    search_fields = ("title", "description", "location")
    ordering = ("created_at",)
    readonly_fields = ("created_at", "resolved_at")
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
    readonly_fields = ("post", "reason", "details", "status", "created_at")
    actions = ("dismiss_reports", "hide_reported_posts")

    @admin.action(description="Dismiss reports (keep posts visible)")
    def dismiss_reports(self, request, queryset):
        reports = queryset.filter(status="pending")
        count = 0

        for report in reports:
            report.status = "dismissed"
            report.save(update_fields=["status"])
            self.log_change(request, report, "Dismissed report.")
            count += 1

        if count:
            self.message_user(
                request,
                f"{count} report(s) dismissed.",
                level="success",
            )
        else:
            self.message_user(
                request,
                "No pending reports were selected.",
                level="warning",
            )

    @admin.action(description="Hide reported posts (remove from public view)")
    def hide_reported_posts(self, request, queryset):
        reports = queryset.filter(status="pending")

        if not reports.exists():
            self.message_user(
                request,
                "No pending reports were selected.",
                level="warning",
            )
            return

        if request.POST.get("confirm_hide") != "yes":
            return TemplateResponse(
                request,
                "admin/board/postreport/confirm_hide.html",
                {
                    **self.admin_site.each_context(request),
                    "title": "Confirm hiding reported posts",
                    "opts": self.model._meta,
                    "reports": reports.select_related("post"),
                },
            )

        count = 0

        for report in reports:
            post = report.post

            if post.status == "approved":
                post.status = "rejected"
                post.save(update_fields=["status"])
                self.log_change(
                    request,
                    report,
                    "Moderator hid the reported post.",
                )

            report.status = "reviewed"
            report.save(update_fields=["status"])
            count += 1

        if count:
            self.message_user(
                request,
                f"{count} report(s) reviewed.",
                level="success",
            )
        else:
            self.message_user(
                request,
                "No pending reports were selected.",
                level="warning",
            )



@admin.register(Subscriber)
class SubscriberAdmin(admin.ModelAdmin):
    list_display = ("email", "active", "created_at")
    list_filter = ("active",)
