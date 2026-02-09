import io
import os
from datetime import date

from django.contrib import messages
from django.core.files.base import ContentFile
from django.shortcuts import get_object_or_404, redirect
from django.views.decorators.http import require_POST
from django.db.models import Prefetch
from django.shortcuts import render
from django.utils.text import slugify
from PIL import ExifTags, Image

from .forms import PhotoEditForm, PhotoUploadForm, SEASON_CHOICES, ZONE_CHOICES
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
	recent_photos = Photo.objects.select_related('season', 'zone')[:50]
	latest_photos = Photo.objects.select_related('season', 'zone')[:12]
	return render(request, 'portfolio/home.html', {
		'recent_photos': recent_photos,
		'latest_photos': latest_photos,
	})


def seasons(request):
	season_nav = [
		{'key': 'spring', 'label': '봄', 'desc': '풀과 꽃이 피어나는 계절'},
		{'key': 'summer', 'label': '여름', 'desc': '파도와 녹음이 짙어지는 계절'},
		{'key': 'autumn', 'label': '가을', 'desc': '단풍이 번지는 계절'},
		{'key': 'winter', 'label': '겨울', 'desc': '눈과 고요가 머무는 계절'},
	]
	key_map = {item['key']: item for item in season_nav}
	active_key = request.GET.get('season', 'spring')
	if active_key not in key_map:
		active_key = 'spring'
	active = key_map[active_key]
	season_obj = Season.objects.filter(name__startswith=active['label']).order_by('order', 'id').first()
	photos_qs = Photo.objects.none()
	if season_obj:
		photos_qs = Photo.objects.filter(season=season_obj).select_related('season', 'zone')
	photos_qs = photos_qs.order_by('-taken_at', '-created_at')
	photo_groups = []
	current_year = None
	for photo in photos_qs:
		year = photo.taken_at.year if photo.taken_at else photo.created_at.year
		if current_year != year:
			photo_groups.append({'year': year, 'photos': []})
			current_year = year
		photo_groups[-1]['photos'].append(photo)
	return render(request, 'portfolio/seasons.html', {
		'season_nav': season_nav,
		'active_key': active_key,
		'active_label': active['label'],
		'active_desc': active['desc'],
		'photo_groups': photo_groups,
	})


def zones(request):
	zone_photos = Prefetch('photo_set', queryset=Photo.objects.select_related('season', 'zone')[:8])
	zones_qs = Zone.objects.prefetch_related(zone_photos)
	return render(request, 'portfolio/zones.html', {'zones': zones_qs})


def archive(request):
	tag_slug = request.GET.get('tag')
	initial = request.GET.get('initial')
	photos = Photo.objects.select_related('season', 'zone').prefetch_related('tags')
	if tag_slug:
		photos = photos.filter(tags__slug=tag_slug)
	tags = Tag.objects.all()
	initials = ['ㄱ', 'ㄴ', 'ㄷ', 'ㄹ', 'ㅁ', 'ㅂ', 'ㅅ', 'ㅇ', 'ㅈ', 'ㅊ', 'ㅋ', 'ㅌ', 'ㅍ', 'ㅎ']
	full_initials = ['ㄱ', 'ㄲ', 'ㄴ', 'ㄷ', 'ㄸ', 'ㄹ', 'ㅁ', 'ㅂ', 'ㅃ', 'ㅅ', 'ㅆ', 'ㅇ', 'ㅈ', 'ㅉ', 'ㅊ', 'ㅋ', 'ㅌ', 'ㅍ', 'ㅎ']
	normalize_initial = {
		'ㄲ': 'ㄱ',
		'ㄸ': 'ㄷ',
		'ㅃ': 'ㅂ',
		'ㅆ': 'ㅅ',
		'ㅉ': 'ㅈ',
	}
	def get_initial(name):
		if not name:
			return ''
		first = name[0]
		code = ord(first) - 0xAC00
		if 0 <= code <= 11171:
			initial = full_initials[code // 588]
			return normalize_initial.get(initial, initial)
		return ''
	if initial in initials:
		tags = [tag for tag in tags if get_initial(tag.name) == initial]
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
		'tag_initials': initials,
		'active_initial': initial,
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
	initial_tags = ', '.join(photo.tags.values_list('name', flat=True))
	initial_season = photo.season.name if photo.season else ''
	initial_zone = photo.zone.name if photo.zone else ''
	initial_date = photo.taken_at or date.today()
	if request.method == 'POST':
		form = PhotoEditForm(request.POST)
		if form.is_valid():
			photo.description = form.cleaned_data['description']
			season_name = form.cleaned_data['season']
			zone_name = form.cleaned_data['zone']
			if season_name:
				season = Season.objects.filter(name=season_name).order_by('id').first()
				if not season:
					season = Season.objects.create(
						name=season_name,
						slug=slugify(season_name, allow_unicode=True),
					)
				photo.season = season
			else:
				photo.season = None
			if zone_name:
				zone = Zone.objects.filter(name=zone_name).order_by('id').first()
				if not zone:
					zone = Zone.objects.create(
						name=zone_name,
						slug=slugify(zone_name, allow_unicode=True),
					)
				photo.zone = zone
			else:
				photo.zone = None
			photo.taken_at = form.cleaned_data['taken_at']
			photo.save()
			tags_value = form.cleaned_data['tags'] or ''
			tag_names = [t.strip() for t in tags_value.split(',') if t.strip()]
			photo.tags.clear()
			for name in tag_names:
				tag, _ = Tag.objects.get_or_create(
					name=name,
					defaults={'slug': slugify(name, allow_unicode=True)},
				)
				photo.tags.add(tag)
			Tag.objects.filter(photo__isnull=True).delete()
			messages.success(request, '사진 정보가 저장되었습니다.')
			return redirect(request.path + f"?next={back_url}")
	else:
		form = PhotoEditForm(initial={
			'description': photo.description,
			'season': initial_season,
			'zone': initial_zone,
			'tags': initial_tags,
			'taken_at': initial_date,
		})
	return render(request, 'portfolio/photo_edit.html', {
		'photo': photo,
		'form': form,
		'exif_entries': exif_entries,
		'back_url': back_url,
		'season_choices': [choice[1] for choice in SEASON_CHOICES if choice[0]],
		'zone_choices': [choice[1] for choice in ZONE_CHOICES if choice[0]],
	})


@require_POST
def delete_photo(request, photo_id):
	photo = get_object_or_404(Photo, id=photo_id)
	if photo.image:
		photo.image.delete(save=False)
	photo.delete()
	Tag.objects.filter(photo__isnull=True).delete()
	next_url = request.POST.get('next')
	return redirect(next_url or 'portfolio:archive')
