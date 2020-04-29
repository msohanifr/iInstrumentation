from django.conf.urls import url
from django.contrib import admin
from django.urls import path, include
from mysite import views

urlpatterns = [
    path('', views.home, name='home'),
    path('test/', views.test, name='test'),
    path('instrument_detail/<str:pk>', views.instrument_detail, name='instrument_detail'),
    path('find_id_based_on_tag/<str:tag>', views.find_id_based_on_tag, name='find_id_based_on_tag'),
    path('loopcheck/', views.loopcheck, name='loopcheck'),
    path('prooftest/<int:pk>', views.prooftest, name='prooftest'),
    path('logout/', views.logout, name='logout'),
    # ajax functions
    path('devicetag_ajax/', views.devicetagajax, name='devicetagajax'),
    path('pid_ajax/', views.pidajax, name='pidajax'),
    path('site_ajax/', views.siteajax, name='siteajax'),
    path('unit_ajax/', views.unitajax, name='unitajax'),
    path('setting/DeviceTypeHtml/', views.devicetypehtmlProoftest,name='devicetypehtml'),
]
