from django.core.management.base import BaseCommand

from portfolio.models import Season, Tag, Zone


class Command(BaseCommand):
    help = "Seed basic seasons, zones, and tags for the portfolio."

    def handle(self, *args, **options):
        seasons = [
            ("봄의 튤립", "spring-tulip", "튤립이 피어나는 봄"),
            ("여름의 녹음", "summer-green", "짙은 녹음의 여름"),
            ("가을의 갈대", "autumn-reed", "바람에 흔들리는 갈대"),
            ("겨울의 설경", "winter-snow", "차분한 눈의 계절"),
        ]
        zones = [
            ("네덜란드 정원", "netherlands", "튤립과 풍차의 정원"),
            ("프랑스 정원", "france", "정제된 선과 색"),
            ("꿈의 다리", "dream-bridge", "산책로와 다리"),
            ("순천만 습지", "suncheon-wetland", "자연의 숨결"),
        ]
        tags = [
            ("빛", "light"),
            ("바람", "wind"),
            ("수면", "water"),
            ("산책", "walk"),
        ]

        for index, (name, slug, description) in enumerate(seasons):
            Season.objects.update_or_create(
                slug=slug,
                defaults={"name": name, "description": description, "order": index + 1},
            )

        for index, (name, slug, description) in enumerate(zones):
            Zone.objects.update_or_create(
                slug=slug,
                defaults={"name": name, "description": description, "order": index + 1},
            )

        for name, slug in tags:
            Tag.objects.update_or_create(slug=slug, defaults={"name": name})

        self.stdout.write(self.style.SUCCESS("Seed data created. Upload photos via admin."))
