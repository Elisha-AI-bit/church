from django.contrib import admin
from .models import Church, UserProfile, Backup, BackupConfiguration
from django.urls import path
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import FileResponse, HttpResponse
from django.utils.html import format_html
from core import backup_utils
import os

@admin.register(Church)
class ChurchAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'is_active', 'created_at']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'church']
    list_filter = ['church']
    search_fields = ['user__username', 'church__name']


@admin.register(Backup)
class BackupAdmin(admin.ModelAdmin):
    list_display = ['filename', 'backup_type', 'status', 'file_size_display', 'created_at', 'created_by', 'action_buttons']
    list_filter = ['backup_type', 'status', 'created_at']
    search_fields = ['filename', 'notes']
    readonly_fields = ['filename', 'created_at', 'created_by', 'file_size', 'status']
    change_list_template = 'admin/core/backup/change_list.html'
    
    def file_size_display(self, obj):
        return f"{obj.file_size_mb} MB"
    file_size_display.short_description = 'Size'
    
    def action_buttons(self, obj):
        if obj.status == 'completed':
            return format_html(
                '<a class="button" href="{}">Download</a> '
                '<a class="button" href="{}">Restore</a>',
                f'/admin/core/backup/{obj.id}/download/',
                f'/admin/core/backup/{obj.id}/restore/'
            )
        return '-'
    action_buttons.short_description = 'Actions'
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('create-backup/', self.admin_site.admin_view(self.create_backup_view), name='core_backup_create'),
            path('<int:backup_id>/download/', self.admin_site.admin_view(self.download_backup_view), name='core_backup_download'),
            path('<int:backup_id>/restore/', self.admin_site.admin_view(self.restore_backup_view), name='core_backup_restore'),
        ]
        return custom_urls + urls
    
    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['create_backup_url'] = '/admin/core/backup/create-backup/'
        return super().changelist_view(request, extra_context=extra_context)
    
    def create_backup_view(self, request):
        if request.method == 'POST':
            backup_type = request.POST.get('backup_type', 'full')
            notes = request.POST.get('notes', '')
            
            try:
                if backup_type == 'database':
                    backup, filepath = backup_utils.create_database_backup(user=request.user, notes=notes)
                elif backup_type == 'media':
                    backup, filepath = backup_utils.create_media_backup(user=request.user, notes=notes)
                else:
                    backup, filepath = backup_utils.create_full_backup(user=request.user, notes=notes)
                
                # Cleanup old backups
                backup_utils.cleanup_old_backups()
                
                messages.success(request, f'Backup created successfully: {backup.filename}')
                return redirect('/admin/core/backup/')
            
            except Exception as e:
                messages.error(request, f'Backup failed: {str(e)}')
                return redirect('/admin/core/backup/')
        
        context = {
            'title': 'Create Backup',
            'opts': self.model._meta,
            'has_view_permission': self.has_view_permission(request),
        }
        return render(request, 'admin/core/backup/create_backup.html', context)
    
    def download_backup_view(self, request, backup_id):
        try:
            backup = Backup.objects.get(id=backup_id)
            filepath = backup_utils.get_backup_file_path(backup)
            
            if not os.path.exists(filepath):
                messages.error(request, 'Backup file not found')
                return redirect('/admin/core/backup/')
            
            response = FileResponse(open(filepath, 'rb'))
            response['Content-Disposition'] = f'attachment; filename="{backup.filename}"'
            return response
        
        except Backup.DoesNotExist:
            messages.error(request, 'Backup not found')
            return redirect('/admin/core/backup/')
    
    def restore_backup_view(self, request, backup_id):
        try:
            backup = Backup.objects.get(id=backup_id)
            filepath = backup_utils.get_backup_file_path(backup)
            
            if not os.path.exists(filepath):
                messages.error(request, 'Backup file not found')
                return redirect('/admin/core/backup/')
            
            if request.method == 'POST':
                confirm = request.POST.get('confirm')
                if confirm == 'yes':
                    try:
                        # Create automatic backup before restore
                        backup_utils.create_full_backup(
                            user=request.user,
                            notes='Automatic backup before restore'
                        )
                        
                        # Perform restore
                        if backup.backup_type == 'database':
                            backup_utils.restore_database(filepath)
                        elif backup.backup_type == 'media':
                            backup_utils.restore_media(filepath)
                        else:
                            backup_utils.restore_full_backup(filepath)
                        
                        messages.success(request, f'Restore completed successfully from: {backup.filename}')
                        return redirect('/admin/core/backup/')
                    
                    except Exception as e:
                        messages.error(request, f'Restore failed: {str(e)}')
                        return redirect('/admin/core/backup/')
            
            context = {
                'title': 'Restore Backup',
                'backup': backup,
                'opts': self.model._meta,
                'has_view_permission': self.has_view_permission(request),
            }
            return render(request, 'admin/core/backup/restore_confirm.html', context)
        
        except Backup.DoesNotExist:
            messages.error(request, 'Backup not found')
            return redirect('/admin/core/backup/')

@admin.register(BackupConfiguration)
class BackupConfigurationAdmin(admin.ModelAdmin):
    list_display = ['auto_backup_enabled', 'frequency', 'preferred_time', 'storage_path', 'backup_type', 'last_run', 'next_run']
    readonly_fields = ['last_run', 'next_run']

    def has_add_permission(self, request):
        # Disable add permission if an instance already exists
        return not BackupConfiguration.objects.exists()

    def has_delete_permission(self, request, obj=None):
        # Disable delete permission to keep the singleton
        return False
