from django.conf.urls import url
from . import views

app_name = 'eshop'

urlpatterns = [
    url('^home/$', views.home, name='home'),
    url(r'^login/$', views.login_user, name='login'),
    url(r'^logout/$', views.logout_user, name='logout'),
    url(r'^register/$', views.UserFormView.as_view(), name = 'register'),
    url(r'^edit/$', views.update_profile, name='edit_profile'),
    url(r'^send/$', views.send_mail, name='send'),
    url(r'^products/$', views.products, name='products'),

]