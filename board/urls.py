from django.urls import path
from . import views

app_name = 'board'

urlpatterns = [
    path(
        "",
        views.home,
        name="home",
    ),
    path(
        "posts/<int:post_id>/report/",
        views.report_post,
        name="report_post",
    ),
    path(
        "posts/edit/<uuid:token>/",
        views.edit_post,
        name="edit_post",
    ),
]