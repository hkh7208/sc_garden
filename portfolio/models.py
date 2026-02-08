from django.db import models
from django.utils import timezone


def photo_upload_path(instance, filename):
	now = timezone.now()
	return f"photos/{now.year}/{now.month:02d}/{filename}"


class Season(models.Model):
	name = models.CharField(max_length=50)
	slug = models.SlugField(unique=True)
	description = models.TextField(blank=True)
	order = models.PositiveSmallIntegerField(default=0)

	class Meta:
		ordering = ['order', 'name']

	def __str__(self):
		return self.name


class Zone(models.Model):
	name = models.CharField(max_length=100)
	slug = models.SlugField(unique=True)
	description = models.TextField(blank=True)
	order = models.PositiveSmallIntegerField(default=0)

	class Meta:
		ordering = ['order', 'name']

	def __str__(self):
		return self.name


class Tag(models.Model):
	name = models.CharField(max_length=50, unique=True)
	slug = models.SlugField(unique=True)

	class Meta:
		ordering = ['name']

	def __str__(self):
		return self.name


class Photo(models.Model):
	title = models.CharField(max_length=120)
	image = models.ImageField(upload_to=photo_upload_path)
	original_filename = models.CharField(max_length=255, blank=True)
	description = models.TextField(blank=True)
	season = models.ForeignKey(Season, on_delete=models.SET_NULL, null=True, blank=True)
	zone = models.ForeignKey(Zone, on_delete=models.SET_NULL, null=True, blank=True)
	tags = models.ManyToManyField(Tag, blank=True)
	taken_at = models.DateField(null=True, blank=True)
	created_at = models.DateTimeField(auto_now_add=True)
	is_featured = models.BooleanField(default=False)

	class Meta:
		ordering = ['-created_at']

	def __str__(self):
		return self.title
