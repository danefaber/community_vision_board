from django.urls import path
from . import views

app_name = 'board'

urlpatterns = [
   path(
       "posts/<int:post_id>/report/",
       views.report_post,
       name="report_post",
   ),
   # path('', views.home, name='home'),                  # Neil
   # path('calendar/', views.calendar, name='calendar'), # Joey
]
