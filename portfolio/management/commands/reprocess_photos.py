import os

from django.core.management.base import BaseCommand
from PIL import Image

from portfolio.models import Photo


class Command(BaseCommand):
	help = "Reprocess existing photos to max 800px width while preserving EXIF."

	def handle(self, *args, **options):
		processed = 0
		skipped = 0
		missing = 0
		for photo in Photo.objects.exclude(image=''):
			image_field = photo.image
			if not image_field:
				missing += 1
				continue
			try:
				path = image_field.path
			except (ValueError, NotImplementedError):
				skipped += 1
				continue
			if not os.path.exists(path):
				missing += 1
				continue

			try:
				image = Image.open(path)
			except OSError:
				skipped += 1
				continue

			exif_bytes = image.info.get('exif')
			if image.mode != 'RGB' and (image.format or '').upper() in ['JPEG', 'JPG']:
				image = image.convert('RGB')
			width, height = image.size
			if width > 800:
				ratio = 800 / float(width)
				image = image.resize((800, int(height * ratio)), Image.LANCZOS)

			save_kwargs = {}
			image_format = (image.format or 'JPEG').upper()
			if image_format in ['JPEG', 'JPG']:
				save_kwargs = {
					'format': 'JPEG',
					'quality': 85,
					'optimize': True,
				}
				if exif_bytes:
					save_kwargs['exif'] = exif_bytes

			image.save(path, **save_kwargs) if save_kwargs else image.save(path)
			processed += 1

		self.stdout.write(
			self.style.SUCCESS(
				f"Reprocessed {processed} photos. Skipped {skipped}, missing {missing}."
			)
		)
