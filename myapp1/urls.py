from django.urls import path, register_converter, re_path

from . import converters
from . import views

register_converter(converters.GroupIdsConverter, 'group_ids_converter')

urlpatterns = [
    path('', views.index.index, name='index'),
    path('donate', views.index.donate, name='donate'),
    path('donate/thx', views.index.donate_thx, name='donate_thx'),
    path('faq', views.index.faq, name='faq'),
    path('maintenance', views.index.maintenance, name='maintenance'),
    path('contact', views.index.contact, name='contact'),
    path('imprint', views.index.imprint, name='imprint'),
    path('privacy', views.index.privacy, name='privacy'),
    path('calendar/<group_ids_converter:group_ids>', views.calendar.choose_groups, name='calendar'),
    path('calendar/modules/<group_ids_converter:group_ids>', views.calendar.choose_modules, name='calendar_modules'),
    re_path(r'^calendar/edit/(?P<calendar_secret>\w{8})$', views.calendar.calendar_edit, name='calendar_edit'),
    path('calendar/link', views.calendar.get_link, name='calendar_link')
]
