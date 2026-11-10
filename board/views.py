from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods

from .models import Post
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
