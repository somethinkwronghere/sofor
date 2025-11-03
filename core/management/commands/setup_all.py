"""
One-shot setup command:
- Runs migrations
- Imports latest bundled SQL dump (firmam_gorev_*.sql) using migrate_from_mysql
- Creates/updates an admin user with a known password
- Optionally collects static files

Usage:
  python manage.py setup_all [--sql your_dump.sql] [--no-static]

Env overrides (optional):
  ADMIN_USERNAME, ADMIN_PASSWORD, ADMIN_NAME
"""
import os
from pathlib import Path
from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.db import transaction
from django.conf import settings


class Command(BaseCommand):
    help = 'Run full setup: migrate, import data, ensure admin, collectstatic'

    def add_arguments(self, parser):
        parser.add_argument('--sql', type=str, help='Path to SQL dump file (optional)')
        parser.add_argument('--no-static', action='store_true', help='Skip collectstatic')

    def handle(self, *args, **options):
        base_dir: Path = settings.BASE_DIR

        # 1) Migrations
        self.stdout.write(self.style.SUCCESS('==> Running migrations'))
        call_command('migrate')

        # 2) Import data via existing migrate_from_mysql command
        sql_file = options.get('sql') or self._find_latest_sql(base_dir)
        if sql_file and Path(sql_file).exists():
            self.stdout.write(self.style.SUCCESS(f'==> Importing data from: {sql_file}'))
            call_command('migrate_from_mysql', sql_file)
        else:
            self.stdout.write(self.style.WARNING('==> No SQL dump found. Skipping data import'))

        # 3) Ensure admin user
        self.stdout.write(self.style.SUCCESS('==> Ensuring admin user'))
        self._ensure_admin_user()

        # 4) Collect static (optional)
        if not options.get('no_static'):
            self.stdout.write(self.style.SUCCESS('==> Collecting static files'))
            call_command('collectstatic', '--noinput')

        self.stdout.write(self.style.SUCCESS('\n✓ Setup completed'))

    def _find_latest_sql(self, base_dir: Path) -> str | None:
        candidates = sorted(base_dir.glob('firmam_gorev_*.sql'), key=lambda p: p.stat().st_mtime, reverse=True)
        return str(candidates[0]) if candidates else None

    @transaction.atomic
    def _ensure_admin_user(self):
        from core.models import Personel

        username = os.environ.get('ADMIN_USERNAME', 'admin')
        password = os.environ.get('ADMIN_PASSWORD', 'Admin123!')
        full_name = os.environ.get('ADMIN_NAME', 'System Admin')

        user, created = Personel.objects.get_or_create(
            kullaniciadi=username,
            defaults={
                'adsoyad': full_name,
                'email': '',
                'yonetici': True,
                'gg': False,
                'girisizni': False,
                'is_active': True,
                'is_staff': True,
                'is_superuser': True,
            },
        )

        # Always set/update password to ensure known credentials
        user.set_password(password)
        user.yonetici = True
        user.is_staff = True
        user.is_superuser = True
        if not user.adsoyad:
            user.adsoyad = full_name
        user.save()

        action = 'created' if created else 'updated'
        self.stdout.write(self.style.SUCCESS(f'   -> Admin {action}: {username}'))
        self.stdout.write(self.style.SUCCESS('      Login credentials prepared.'))


