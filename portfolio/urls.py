from django.urls import path

from . import views

app_name = 'portfolio'

urlpatterns = [
    path('', views.home, name='home'),
    path('seasons/', views.seasons, name='seasons'),
    path('zones/', views.zones, name='zones'),
    path('archive/', views.archive, name='archive'),
    path('management/', views.management, name='management'),
    path('api/zones/', views.get_zones, name='get_zones'),
    path('api/zones/add/', views.add_zone, name='add_zone'),
    path('api/zones/<int:zone_id>/delete/', views.delete_zone, name='delete_zone'),
    path('api/photos/bulk-edit/', views.bulk_edit_photos, name='bulk_edit_photos'),
    path('archive/edit/<int:photo_id>/', views.edit_photo, name='edit_photo'),
    path('archive/delete/<int:photo_id>/', views.delete_photo, name='delete_photo'),
    path('about/', views.about, name='about'),
]
