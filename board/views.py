from django.contrib import messages
from django.conf import settings
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods

from .edit_forms import PostEditForm
from .edit_links import send_edit_link
from .models import Post, Category
from .post_forms import PostForm
from .post_limits import PostRateLimitExceeded
from .post_submission import CaptchaVerificationFailed, submit_post
from .report_forms import PostReportForm

@require_http_methods(["GET", "POST"])
def report_post(request, post_id):
    post = get_object_or_404(
        Post,
        pk=post_id,
        status="approved"
    )

    if request.method == "POST":
        form = PostReportForm(request.POST)

        if form.is_valid():
            report = form.save(commit=False)
            report.post = post
            report.status = "pending"
            report.save()

            messages.success(
                request,
                "Your report was submitted for moderator review."
            )

            return redirect("board:report_post", post_id=post.pk)

    else:
        form = PostReportForm()

    return render(
        request,
        "board/report_post.html",
        {
            "post": post,
            "form": form,
        }
    )

@require_http_methods(["GET", "POST"])
def edit_post(request, token):
    post = get_object_or_404(
        Post,
        edit_token=token,
    )

    if request.method == "POST":
        form = PostEditForm(request.POST, instance=post)

        if form.is_valid():
            if form.has_changed():
                edited_post = form.save(commit=False)

                # Edits must be reviewed by a moderator.
                edited_post.status = "pending"
                edited_post.save()

                messages.success(
                    request,
                    "Your changes were saved and sent for moderator review."
                )
            else:
                messages.info(
                    request,
                    "No changes were made."
                )

            return redirect("board:edit_post", token=post.edit_token)

    else:
        form = PostEditForm(instance=post)

    return render(
        request,
        "board/edit_post.html",
        {
            "post": post,
            "form": form,
        }
    )

def home(request):
    # Get approved posts, newest first
    posts = Post.objects.filter(
        status="approved"
    ).order_by("-created_at")

    # Get all categories
    categories = Category.objects.all()

    return render(
        request,
        "board/home.html",
        {
            "posts": posts,
            "categories": categories,
        }
    )
def category_posts(request, category_id):
    # Find the selected category
    category = get_object_or_404(Category, pk=category_id)

    # Get approved posts in this category
    posts = Post.objects.filter(
        category=category,
        status="approved"
    ).order_by("-created_at")

    return render(
        request,
        "board/category_posts.html",
        {
            "category": category,
            "posts": posts,
        }
    )
def submit_post_view(request):
    if request.method == "POST":
        form = PostForm(request.POST)

        if form.is_valid():
            try:
                post = submit_post(request, lambda: form.save())
            except CaptchaVerificationFailed:
                form.add_error(None, "Please complete the CAPTCHA.")
            except PostRateLimitExceeded:
                form.add_error(
                    None,
                    "You've reached the limit of 5 posts per hour. Try again later."
                )
            else:
                send_edit_link(request, post)
                return redirect("board:post_submitted")
    else:
        form = PostForm()

    return render(request, "board/submit_post.html", {
        "form": form,
        "recaptcha_site_key": settings.RECAPTCHA_SITE_KEY,
    })


def post_submitted(request):
    return render(request, "board/post_submitted.html")