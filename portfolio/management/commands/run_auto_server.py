import os

from django.core.management import BaseCommand, call_command

from config.runtime_profile import detect_runtime_profile, get_auto_addrport


class Command(BaseCommand):
    help = '런타임 환경(local/nas)을 자동 감지해 적절한 포트로 runserver를 실행합니다.'

    def handle(self, *args, **options):
        profile = detect_runtime_profile()
        os.environ['DB_HOST_MODE'] = profile
        addrport = get_auto_addrport(profile)

        self.stdout.write(self.style.SUCCESS(
            f'Auto profile={profile}, DB_HOST_MODE={profile}, addrport={addrport}'
        ))
        call_command('runserver', addrport)
