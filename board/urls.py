from django.urls import path

from . import views

urlpatterns = [
    path(
        "posts/<int:post_id>/report/",
        views.report_post,
        name="report_post",
    ),
]
