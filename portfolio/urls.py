from django.urls import path

from . import views

app_name = 'portfolio'

urlpatterns = [
    path('', views.home, name='home'),
    path('seasons/', views.seasons, name='seasons'),
    path('zones/', views.zones, name='zones'),
    path('archive/', views.archive, name='archive'),
    path('archive/edit/<int:photo_id>/', views.edit_photo, name='edit_photo'),
    path('archive/delete/<int:photo_id>/', views.delete_photo, name='delete_photo'),
    path('about/', views.about, name='about'),
]
