from django.conf.urls import url
from django.contrib import admin
from django.urls import path, include

from mysite.core import views

urlpatterns = [
    url('', include('social_django.urls', namespace='social')),
    # path('accounts/register', views.register, name='register'),
    path('ajax/', views.ajax_order, name='ajax_test'),
    path('accounts/update_profile_after_initial/', views.update_profile_after_initial,
         name='update_profile_after_initial'),
    path('account/update_profile/', views.update_profile, name='update_profile'),
    path('home/', views.home, name='home'),
    path('signup/', views.signup, name='signup'),
    path('order/', views.order_page, name='order'),
    path('cart/', views.cart_page, name='cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('pay/', views.pay.as_view(), name='pay'),
    path('charged/', views.charged, name='charged'),
    # path('secret2/', views.SecretPage.as_view(), name='secret2'),
    path('signup_additional/', views.signup_additional, name='signup_additional'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('herror/', views.handler500, name='herror'),
    path('admin/', admin.site.urls),
]
