from django.conf.urls import url
from . import views

app_name = 'eshop'

urlpatterns = [
    url('^home/$', views.home, name='home'),
    url(r'^login/$', views.login_user, name='login'),
    url(r'^register/$', views.UserFormView.as_view(), name = 'register'),
    url(r'^edit/(?P<username>\w+)/$', views.update_profile, name='edit_profile'),
    url(r'^send/$', views.send_mail, name='send'),

]