import os
import json
import zipfile
import shutil
from datetime import datetime
from django.conf import settings
from django.core.management import call_command
from pathlib import Path
import subprocess

# Backup directory configuration
BACKUP_DIR = getattr(settings, 'BACKUP_DIR', os.path.join(settings.BASE_DIR, 'backups'))
MAX_BACKUPS = getattr(settings, 'MAX_BACKUPS', 10)

# Ensure backup directory exists
os.makedirs(BACKUP_DIR, exist_ok=True)


def get_backup_dir():
    """Get the current backup directory from configuration or settings"""
    from core.models import BackupConfiguration
    config = BackupConfiguration.objects.first()
    if config and config.storage_path:
        # Ensure custom directory exists
        path = config.storage_path
        if not os.path.exists(path):
            try:
                os.makedirs(path, exist_ok=True)
            except Exception:
                # Fallback to default if custom path is invalid/inaccessible
                return BACKUP_DIR
        return path
    return BACKUP_DIR


def create_database_backup(user=None, notes=''):
    """Create a database backup using dumpdata"""
    from core.models import Backup
    
    current_backup_dir = get_backup_dir()
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'db_backup_{timestamp}.json'
    filepath = os.path.join(current_backup_dir, filename)
    
    # Create backup record
    backup = Backup.objects.create(
        filename=filename,
        absolute_path=filepath,
        created_by=user,
        backup_type='database',
        status='in_progress',
        notes=notes
    )
    
    try:
        # Dump database to JSON
        with open(filepath, 'w', encoding='utf-8') as f:
            call_command('dumpdata', 
                        exclude=['contenttypes', 'auth.permission', 'sessions.session'],
                        indent=2,
                        stdout=f)
        
        # Update backup record
        backup.file_size = os.path.getsize(filepath)
        backup.status = 'completed'
        backup.save()
        
        return backup, filepath
    
    except Exception as e:
        backup.status = 'failed'
        backup.notes = f"{backup.notes}\nError: {str(e)}"
        backup.save()
        raise


def create_media_backup(user=None, notes=''):
    """Create a ZIP archive of media files"""
    from core.models import Backup
    
    current_backup_dir = get_backup_dir()
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'media_backup_{timestamp}.zip'
    filepath = os.path.join(current_backup_dir, filename)
    
    # Create backup record
    backup = Backup.objects.create(
        filename=filename,
        absolute_path=filepath,
        created_by=user,
        backup_type='media',
        status='in_progress',
        notes=notes
    )
    
    try:
        media_root = settings.MEDIA_ROOT
        
        # Create ZIP archive
        with zipfile.ZipFile(filepath, 'w', zipfile.ZIP_DEFLATED) as zipf:
            if os.path.exists(media_root):
                for root, dirs, files in os.walk(media_root):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, media_root)
                        zipf.write(file_path, arcname)
        
        # Update backup record
        backup.file_size = os.path.getsize(filepath)
        backup.status = 'completed'
        backup.save()
        
        return backup, filepath
    
    except Exception as e:
        backup.status = 'failed'
        backup.notes = f"{backup.notes}\nError: {str(e)}"
        backup.save()
        raise


def create_full_backup(user=None, notes=''):
    """Create a full backup (database + media)"""
    from core.models import Backup
    
    current_backup_dir = get_backup_dir()
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'full_backup_{timestamp}.zip'
    filepath = os.path.join(current_backup_dir, filename)
    
    # Create backup record
    backup = Backup.objects.create(
        filename=filename,
        absolute_path=filepath,
        created_by=user,
        backup_type='full',
        status='in_progress',
        notes=notes
    )
    
    try:
        # Create temporary directory for backup components
        temp_dir = os.path.join(current_backup_dir, f'temp_{timestamp}')
        os.makedirs(temp_dir, exist_ok=True)
        
        # Create database dump
        db_file = os.path.join(temp_dir, 'database.json')
        with open(db_file, 'w', encoding='utf-8') as f:
            call_command('dumpdata',
                        exclude=['contenttypes', 'auth.permission', 'sessions.session'],
                        indent=2,
                        stdout=f)
        
        # Create ZIP with database and media
        with zipfile.ZipFile(filepath, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Add database dump
            zipf.write(db_file, 'database.json')
            
            # Add media files
            media_root = settings.MEDIA_ROOT
            if os.path.exists(media_root):
                for root, dirs, files in os.walk(media_root):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.join('media', os.path.relpath(file_path, media_root))
                        zipf.write(file_path, arcname)
        
        # Cleanup temp directory
        shutil.rmtree(temp_dir)
        
        # Update backup record
        backup.file_size = os.path.getsize(filepath)
        backup.status = 'completed'
        backup.save()
        
        return backup, filepath
    
    except Exception as e:
        backup.status = 'failed'
        backup.notes = f"{backup.notes}\nError: {str(e)}"
        backup.save()
        
        # Cleanup
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
        
        raise


def restore_database(backup_file_path):
    """Restore database from JSON backup"""
    if not os.path.exists(backup_file_path):
        raise FileNotFoundError(f"Backup file not found: {backup_file_path}")
    
    try:
        # Flush existing data (except users and permissions)
        call_command('flush', '--no-input', verbosity=0)
        
        # Load data from backup
        call_command('loaddata', backup_file_path, verbosity=2)
        
        return True
    except Exception as e:
        raise Exception(f"Database restore failed: {str(e)}")


def restore_media(backup_file_path):
    """Restore media files from ZIP backup"""
    if not os.path.exists(backup_file_path):
        raise FileNotFoundError(f"Backup file not found: {backup_file_path}")
    
    try:
        media_root = settings.MEDIA_ROOT
        
        # Extract ZIP to media directory
        with zipfile.ZipFile(backup_file_path, 'r') as zipf:
            zipf.extractall(media_root)
        
        return True
    except Exception as e:
        raise Exception(f"Media restore failed: {str(e)}")


def restore_full_backup(backup_file_path):
    """Restore full backup (database + media)"""
    if not os.path.exists(backup_file_path):
        raise FileNotFoundError(f"Backup file not found: {backup_file_path}")
    
    try:
        # Create temporary extraction directory
        temp_dir = os.path.join(BACKUP_DIR, f'restore_temp_{datetime.now().strftime("%Y%m%d_%H%M%S")}')
        os.makedirs(temp_dir, exist_ok=True)
        
        # Extract backup
        with zipfile.ZipFile(backup_file_path, 'r') as zipf:
            zipf.extractall(temp_dir)
        
        # Restore database
        db_file = os.path.join(temp_dir, 'database.json')
        if os.path.exists(db_file):
            call_command('flush', '--no-input', verbosity=0)
            call_command('loaddata', db_file, verbosity=2)
        
        # Restore media files
        media_backup_dir = os.path.join(temp_dir, 'media')
        if os.path.exists(media_backup_dir):
            media_root = settings.MEDIA_ROOT
            # Clear existing media
            if os.path.exists(media_root):
                shutil.rmtree(media_root)
            # Copy backup media
            shutil.copytree(media_backup_dir, media_root)
        
        # Cleanup
        shutil.rmtree(temp_dir)
        
        return True
    except Exception as e:
        # Cleanup on error
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
        raise Exception(f"Full restore failed: {str(e)}")


def cleanup_old_backups():
    """Remove old backups exceeding MAX_BACKUPS limit"""
    from core.models import Backup
    
    backups = Backup.objects.filter(status='completed').order_by('-created_at')
    
    if backups.count() > MAX_BACKUPS:
        old_backups = backups[MAX_BACKUPS:]
        for backup in old_backups:
            # Delete file
            filepath = backup.absolute_path or os.path.join(BACKUP_DIR, backup.filename)
            if os.path.exists(filepath):
                os.remove(filepath)
            # Delete record
            backup.delete()


def get_backup_file_path(backup):
    """Get full path to backup file"""
    return backup.absolute_path or os.path.join(BACKUP_DIR, backup.filename)
