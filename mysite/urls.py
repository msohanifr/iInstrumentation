from django.conf.urls import url
from django.contrib import admin
from django.urls import path, include

from mysite.core import views

urlpatterns = [
    url('', include('social_django.urls', namespace='social')),
    path('accounts/update_profile_after_initial/', views.update_profile_after_initial,
         name='update_profile_after_initial'),
    url(r'^activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        views.activate, name='activate'),
    path('sms/', views.send_sms, name='sendsms'),
    path('sms_sent/', views.sms_sent, name='smssent'),
    url(r'^phone_activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        views.phone_activate, name='phone_activate'),
    path('sendemailconfirmation/', views.send_email_confirmation, name='send_email_confirmation'),
    path('confirmemailsent', views.confirm_email_sent, name='confirmemailsent'),
    path('home/', views.home, name='home'),
    path('signup/', views.signup, name='signup'),
    path('signup_additional/', views.signup_additional, name='signup_additional'),
    path('profile/', views.profile, name='profile'),
    path('account/update_profile/', views.update_profile, name='update_profile'),
    path('order/', views.order_page, name='order'),
    path('order_history', views.order_history, name='order_history'),
    path('ajax/', views.ajax_order, name='ajax_test'),
    path('cart/', views.cart_page, name='cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('pay/', views.pay.as_view(), name='pay'),
    path('charged/', views.charged, name='charged'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('support/', views.support, name='support'),
    path('herror/', views.handler500, name='herror'),
    path('admin/', admin.site.urls),
    path('logout/', views.logout, name='logout'),
]
