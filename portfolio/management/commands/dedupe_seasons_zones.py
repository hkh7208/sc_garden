from django.core.management.base import BaseCommand
from django.db import transaction

from portfolio.models import Photo, Season, Zone


class Command(BaseCommand):
	help = "Deduplicate seasons and zones by name, keeping the oldest record."

	@transaction.atomic
	def handle(self, *args, **options):
		season_map = {}
		for season in Season.objects.order_by('id'):
			season_map.setdefault(season.name, season)

		season_deleted = 0
		for season in Season.objects.order_by('id'):
			keeper = season_map.get(season.name)
			if keeper and keeper.id != season.id:
				Photo.objects.filter(season=season).update(season=keeper)
				season.delete()
				season_deleted += 1

		zone_map = {}
		for zone in Zone.objects.order_by('id'):
			zone_map.setdefault(zone.name, zone)

		zone_deleted = 0
		for zone in Zone.objects.order_by('id'):
			keeper = zone_map.get(zone.name)
			if keeper and keeper.id != zone.id:
				Photo.objects.filter(zone=zone).update(zone=keeper)
				zone.delete()
				zone_deleted += 1

		self.stdout.write(
			self.style.SUCCESS(
				f"Seasons removed: {season_deleted}, Zones removed: {zone_deleted}."
			)
		)
