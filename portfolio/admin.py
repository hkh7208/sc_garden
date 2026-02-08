from django.contrib import admin

from .models import Photo, Season, Tag, Zone


@admin.register(Season)
class SeasonAdmin(admin.ModelAdmin):
	list_display = ('name', 'order')
	prepopulated_fields = {'slug': ('name',)}


@admin.register(Zone)
class ZoneAdmin(admin.ModelAdmin):
	list_display = ('name', 'order')
	prepopulated_fields = {'slug': ('name',)}


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
	list_display = ('name',)
	prepopulated_fields = {'slug': ('name',)}


@admin.register(Photo)
class PhotoAdmin(admin.ModelAdmin):
	list_display = ('title', 'season', 'zone', 'is_featured', 'created_at')
	list_filter = ('season', 'zone', 'is_featured', 'tags')
	search_fields = ('title', 'description')
