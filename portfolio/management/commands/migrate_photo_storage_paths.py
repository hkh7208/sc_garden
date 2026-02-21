import os

from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.core.management.base import BaseCommand, CommandError

from portfolio.models import Photo


class Command(BaseCommand):
	help = '기존 공용 이미지 경로(photos/...)를 환경별 경로(photos/local|nas/...)로 이관합니다.'

	def add_arguments(self, parser):
		parser.add_argument('--target', choices=['local', 'nas'], required=True)
		parser.add_argument('--commit', action='store_true', help='실제 파일 이동 및 DB 반영 수행')

	def _split_old_path(self, image_name):
		if not image_name or not image_name.startswith('photos/'):
			return None
		tail = image_name[len('photos/'):]
		if tail.startswith('local/') or tail.startswith('nas/'):
			return None
		return tail

	def handle(self, *args, **options):
		target = options['target']
		commit = options['commit']

		if not hasattr(settings, 'MEDIA_ROOT') or not settings.MEDIA_ROOT:
			raise CommandError('MEDIA_ROOT 설정이 필요합니다.')

		moved = 0
		skipped = 0
		missing = 0
		errors = 0
		candidates = 0

		photos = Photo.objects.exclude(image='').order_by('id')
		for photo in photos:
			old_name = photo.image.name
			tail = self._split_old_path(old_name)
			if not tail:
				skipped += 1
				continue

			candidates += 1
			new_name = f'photos/{target}/{tail}'

			if not commit:
				self.stdout.write(f'[DRY-RUN] photo_id={photo.id}: {old_name} -> {new_name}')
				continue

			try:
				if default_storage.exists(old_name):
					with default_storage.open(old_name, 'rb') as source:
						saved_name = default_storage.save(new_name, ContentFile(source.read()))
					if saved_name != old_name and default_storage.exists(old_name):
						default_storage.delete(old_name)
					photo.image.name = saved_name
					photo.save(update_fields=['image'])
					moved += 1
				else:
					missing += 1
					self.stdout.write(self.style.WARNING(
						f'[MISSING] photo_id={photo.id}: 파일 없음 {old_name}'
					))
			except OSError as exc:
				errors += 1
				self.stdout.write(self.style.ERROR(
					f'[ERROR] photo_id={photo.id}: {old_name} -> {new_name} ({exc})'
				))

		mode = 'COMMIT' if commit else 'DRY-RUN'
		self.stdout.write(self.style.SUCCESS(
			f'[{mode}] target={target}, candidates={candidates}, moved={moved}, skipped={skipped}, missing={missing}, errors={errors}'
		))
