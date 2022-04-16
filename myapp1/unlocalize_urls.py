from django.urls import path, re_path
from . import views

urlpatterns = [
    path('groups', views.calendar.get_groups, name='subjects'),
    path('studium_generale', views.calendar.get_studium_generale, name='studium_generale'),
    re_path(r'^(?P<calendar_secret>\w{8})$', views.calendar.get, name='calender_get'),
]
