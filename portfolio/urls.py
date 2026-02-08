from django.urls import path

from . import views

app_name = 'portfolio'

urlpatterns = [
    path('', views.home, name='home'),
    path('seasons/', views.seasons, name='seasons'),
    path('zones/', views.zones, name='zones'),
    path('archive/', views.archive, name='archive'),
    path('about/', views.about, name='about'),
]
