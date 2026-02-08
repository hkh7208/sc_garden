from django.db.models import Prefetch
from django.shortcuts import render

from .models import Photo, Season, Tag, Zone


def home(request):
	featured_qs = Photo.objects.filter(is_featured=True).select_related('season', 'zone')
	featured_list = list(featured_qs[:5])
	if len(featured_list) < 3:
		latest_list = list(Photo.objects.select_related('season', 'zone')[:5])
		seen_ids = {photo.id for photo in featured_list}
		for photo in latest_list:
			if photo.id not in seen_ids:
				featured_list.append(photo)
				seen_ids.add(photo.id)
			if len(featured_list) >= 5:
				break
	latest_photos = Photo.objects.select_related('season', 'zone')[:12]
	return render(request, 'portfolio/home.html', {
		'featured': featured_list,
		'latest_photos': latest_photos,
	})


def seasons(request):
	season_photos = Prefetch('photo_set', queryset=Photo.objects.select_related('season', 'zone')[:8])
	seasons_qs = Season.objects.prefetch_related(season_photos)
	return render(request, 'portfolio/seasons.html', {'seasons': seasons_qs})


def zones(request):
	zone_photos = Prefetch('photo_set', queryset=Photo.objects.select_related('season', 'zone')[:8])
	zones_qs = Zone.objects.prefetch_related(zone_photos)
	return render(request, 'portfolio/zones.html', {'zones': zones_qs})


def archive(request):
	tag_slug = request.GET.get('tag')
	photos = Photo.objects.select_related('season', 'zone').prefetch_related('tags')
	if tag_slug:
		photos = photos.filter(tags__slug=tag_slug)
	tags = Tag.objects.all()
	return render(request, 'portfolio/archive.html', {
		'photos': photos,
		'tags': tags,
		'active_tag': tag_slug,
	})


def about(request):
	return render(request, 'portfolio/about.html')
