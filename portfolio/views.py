import io
import os

from django.core.files.base import ContentFile
from django.shortcuts import get_object_or_404, redirect
from django.views.decorators.http import require_POST
from django.db.models import Prefetch
from django.shortcuts import render
from PIL import ExifTags, Image

from .forms import PhotoUploadForm
from .models import Photo, Season, Tag, Zone


def _resize_upload(uploaded_file, max_width=800):
	image = Image.open(uploaded_file)
	exif_bytes = image.info.get('exif')
	image_format = (image.format or 'JPEG').upper()
	if image_format in ['JPEG', 'JPG'] and image.mode != 'RGB':
		image = image.convert('RGB')
	width, height = image.size
	if width > max_width:
		ratio = max_width / float(width)
		new_size = (max_width, int(height * ratio))
		image = image.resize(new_size, Image.LANCZOS)
	output = io.BytesIO()
	base_name, extension = os.path.splitext(uploaded_file.name)
	if image_format in ['JPEG', 'JPG']:
		save_kwargs = {
			'format': 'JPEG',
			'quality': 85,
			'optimize': True,
		}
		if exif_bytes:
			save_kwargs['exif'] = exif_bytes
		image.save(output, **save_kwargs)
		if extension.lower() not in ['.jpg', '.jpeg']:
			extension = '.jpg'
	else:
		image.save(output, format=image_format)
	output.seek(0)
	return ContentFile(output.read()), f"{base_name}{extension}"


def _get_exif_data(photo):
	if not photo.image:
		return []
	try:
		image = Image.open(photo.image.path)
		exif = image.getexif()
		if not exif:
			return []
		entries = []
		for tag_id, value in exif.items():
			label = ExifTags.TAGS.get(tag_id, str(tag_id))
			entries.append((label, str(value)))
		return entries
	except (FileNotFoundError, OSError):
		return []


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
	upload_form = PhotoUploadForm()
	duplicate_names = []
	upload_error = None
	uploaded_count = 0
	if request.method == 'POST':
		upload_form = PhotoUploadForm(request.POST, request.FILES)
		files = request.FILES.getlist('images')
		if not files:
			upload_error = '업로드할 파일을 선택해주세요.'
		elif len(files) > 50:
			upload_error = '한번에 최대 50장까지 업로드할 수 있습니다.'
		else:
			existing_names = set()
			for photo in Photo.objects.only('original_filename', 'image'):
				if photo.original_filename:
					existing_names.add(photo.original_filename)
				elif photo.image:
					existing_names.add(os.path.basename(photo.image.name))
			for uploaded in files:
				original_name = uploaded.name
				if original_name in existing_names:
					duplicate_names.append(original_name)
					continue
				resized_file, stored_name = _resize_upload(uploaded)
				title = os.path.splitext(original_name)[0]
				photo = Photo(title=title, original_filename=original_name)
				photo.image.save(stored_name, resized_file, save=False)
				photo.save()
				uploaded_count += 1
				existing_names.add(original_name)
	return render(request, 'portfolio/archive.html', {
		'photos': photos,
		'tags': tags,
		'active_tag': tag_slug,
		'upload_form': upload_form,
		'duplicate_names': duplicate_names,
		'upload_error': upload_error,
		'uploaded_count': uploaded_count,
	})


def about(request):
	return render(request, 'portfolio/about.html')


def edit_photo(request, photo_id):
	photo = get_object_or_404(Photo, id=photo_id)
	exif_entries = _get_exif_data(photo)
	back_url = request.GET.get('next') or 'portfolio:archive'
	return render(request, 'portfolio/photo_edit.html', {
		'photo': photo,
		'exif_entries': exif_entries,
		'back_url': back_url,
	})


@require_POST
def delete_photo(request, photo_id):
	photo = get_object_or_404(Photo, id=photo_id)
	if photo.image:
		photo.image.delete(save=False)
	photo.delete()
	next_url = request.POST.get('next')
	return redirect(next_url or 'portfolio:archive')
