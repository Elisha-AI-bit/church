from django.core.management.base import BaseCommand
from django.utils import timezone
from core.models import BackupConfiguration
from core import backup_utils
from datetime import timedelta

class Command(BaseCommand):
    help = 'Runs automated backups based on BackupConfiguration'

    def handle(self, *args, **options):
        config = BackupConfiguration.objects.first()
        
        if not config or not config.auto_backup_enabled:
            self.stdout.write(self.style.WARNING('Auto-backup is disabled or not configured.'))
            return

        now = timezone.now()
        
        # Check if next_run is set and if it's time to run
        if config.next_run and now < config.next_run:
            self.stdout.write(self.style.NOTICE(f'Next backup is scheduled for {config.next_run}. Skipping.'))
            return

        self.stdout.write(self.style.SUCCESS(f'Starting automated {config.backup_type} backup...'))
        
        try:
            notes = f"Automated {config.frequency} backup"
            if config.backup_type == 'database':
                backup, filepath = backup_utils.create_database_backup(notes=notes)
            elif config.backup_type == 'media':
                backup, filepath = backup_utils.create_media_backup(notes=notes)
            else:
                backup, filepath = backup_utils.create_full_backup(notes=notes)
            
            # Update last_run and calculate next_run
            config.last_run = now
            
            # Combine tomorrow/next date with preferred_time
            import datetime
            def get_next_scheduled(base_date, delta):
                target_date = base_date + delta
                return timezone.make_aware(
                    datetime.datetime.combine(target_date, config.preferred_time)
                )

            if config.frequency == 'daily':
                config.next_run = get_next_scheduled(now.date(), timedelta(days=1))
            elif config.frequency == 'weekly':
                config.next_run = get_next_scheduled(now.date(), timedelta(weeks=1))
            elif config.frequency == 'monthly':
                config.next_run = get_next_scheduled(now.date(), timedelta(days=30))
            
            config.save()
            
            # Cleanup old backups
            backup_utils.cleanup_old_backups()
            
            self.stdout.write(self.style.SUCCESS(f'Automated backup completed: {backup.filename}'))
            self.stdout.write(self.style.SUCCESS(f'Next backup scheduled for: {config.next_run}'))
            
        except Exception as e:
            self.stderr.write(self.style.ERROR(f'Automated backup failed: {str(e)}'))
