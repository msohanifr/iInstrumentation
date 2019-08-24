from django.conf.urls import url
from django.contrib import admin
from django.urls import path, include
from mysite.core import views
from mysite.core.views import urlsecret

urlpatterns = [
    url('', include('social_django.urls', namespace='social')),
    path('accounts/update_profile_after_initial/', views.update_profile_after_initial,
         name='update_profile_after_initial'),
    url(r'^activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        views.activate, name='activate'),
    path(urlsecret.SECRET_CODE + '/sms/', views.send_sms, name='sendsms'),
    path('qetuadgj85hj/sms_sent/', views.sms_sent, name='smssent'),
    url(r'^phone_activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        views.phone_activate, name='phone_activate'),
    path(urlsecret.SECRET_CODE + '/sendemailconfirmation/', views.send_email_confirmation,
         name='send_email_confirmation'),
    path(urlsecret.SECRET_CODE + '/confirmemailsent', views.confirm_email_sent, name='confirmemailsent'),
    path(urlsecret.SECRET_CODE + '/home/', views.home, name='home'),
    path(urlsecret.SECRET_CODE + '/signup/', views.signup, name='signup'),
    path(urlsecret.SECRET_CODE + '/signup_additional/', views.signup_additional, name='signup_additional'),
    path(urlsecret.SECRET_CODE + '/profile/', views.profile, name='profile'),
    path(urlsecret.SECRET_CODE + '/account/update_profile/', views.update_profile, name='update_profile'),
    path(urlsecret.SECRET_CODE + '/order/', views.order_page, name='order'),
    path(urlsecret.SECRET_CODE + '/order_history', views.order_history, name='order_history'),
    path('smsajax/', views.ajax_sms, name='smsajax'),
    path('ajax/', views.ajax_order, name='ajax_test'),
    path('profileajax/', views.profile_ajax, name='profile_ajax'),
    path(urlsecret.SECRET_CODE + '/cart/', views.cart_page, name='cart'),
    path(urlsecret.SECRET_CODE + '/checkout/', views.checkout, name='checkout'),
    path(urlsecret.SECRET_CODE + '/pay/', views.pay.as_view(), name='pay'),
    path(urlsecret.SECRET_CODE + '/charged/', views.charged, name='charged'),
    path('accounts/', include('django.contrib.auth.urls')),
    path(urlsecret.SECRET_CODE + '/support/', views.support, name='support'),
    path(urlsecret.SECRET_CODE + '/admin/', admin.site.urls),
    path(urlsecret.SECRET_CODE + '/logout/', views.logout, name='logout'),
]
