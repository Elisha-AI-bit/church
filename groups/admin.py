from django.contrib import admin
from .models import Group, GroupLeadership, GroupMembership
import csv
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from django.urls import path


class GroupLeadershipInline(admin.TabularInline):
    model = GroupLeadership
    extra = 1


class GroupMembershipInline(admin.TabularInline):
    model = GroupMembership
    extra = 1
    fields = ['member', 'joined_date', 'is_active', 'notes']
    autocomplete_fields = ['member']


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ['name', 'meeting_schedule']
    list_display_links = ['name']
    search_fields = ['name']
    inlines = [GroupLeadershipInline, GroupMembershipInline]
    
    change_list_template = "admin/groups/group_changelist.html"
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('import-csv/', self.admin_site.admin_view(self.import_csv), name='group_import_csv'),
            path('download-template/', self.admin_site.admin_view(self.download_template), name='group_download_template'),
        ]
        return custom_urls + urls
    
    def download_template(self, request):
        """Download CSV template for group import"""
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="group_import_template.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['name', 'description', 'meeting_schedule'])
        writer.writerow(["Men's Christian Fellowship", 'Fellowship for men', 'Every first Sunday at 2:00 PM'])
        writer.writerow(["Women's Christian Fellowship", 'Fellowship for women', 'Every second Sunday at 2:00 PM'])
        writer.writerow(['Youth Group', 'Activities for youth', 'Every Saturday at 10:00 AM'])
        
        return response
    
    def import_csv(self, request):
        """Import groups from CSV file"""
        if request.method == "POST":
            csv_file = request.FILES.get('csv_file')
            
            if not csv_file:
                messages.error(request, 'Please select a CSV file to upload.')
                return redirect("..")
            
            if not csv_file.name.endswith('.csv'):
                messages.error(request, 'File must be a CSV file.')
                return redirect("..")
            
            try:
                # Try multiple encodings to handle different CSV formats
                raw_data = csv_file.read()
                decoded_file = None
                
                for encoding in ['utf-8-sig', 'utf-8', 'latin-1', 'cp1252']:
                    try:
                        decoded_file = raw_data.decode(encoding).splitlines()
                        break
                    except UnicodeDecodeError:
                        continue
                
                if decoded_file is None:
                    messages.error(request, 'Unable to decode CSV file. Please ensure it is saved in UTF-8 format.')
                    return redirect("..")
                
                reader = csv.DictReader(decoded_file)
                
                created_count = 0
                updated_count = 0
                errors = []
                
                for row_num, row in enumerate(reader, start=2):
                    try:
                        name = row.get('name', '').strip()
                        description = row.get('description', '').strip()
                        meeting_schedule = row.get('meeting_schedule', '').strip()
                        
                        if not name:
                            errors.append(f"Row {row_num}: Name is required")
                            continue
                        
                        # Create or update group
                        group, created = Group.objects.update_or_create(
                            name=name,
                            defaults={
                                'description': description,
                                'meeting_schedule': meeting_schedule,
                            }
                        )
                        
                        if created:
                            created_count += 1
                        else:
                            updated_count += 1
                            
                    except Exception as e:
                        errors.append(f"Row {row_num}: {str(e)}")
                
                # Show results
                if created_count > 0:
                    messages.success(request, f'Successfully created {created_count} group(s).')
                if updated_count > 0:
                    messages.info(request, f'Updated {updated_count} existing group(s).')
                if errors:
                    for error in errors[:5]:  # Show first 5 errors
                        messages.error(request, error)
                    if len(errors) > 5:
                        messages.error(request, f'...and {len(errors) - 5} more errors.')
                
                return redirect("..")
                
            except Exception as e:
                messages.error(request, f'Error processing CSV file: {str(e)}')
                return redirect("..")
        
        # GET request - show upload form
        return render(request, "admin/groups/import_csv.html")



@admin.register(GroupLeadership)
class GroupLeadershipAdmin(admin.ModelAdmin):
    list_display = ['group', 'member', 'role', 'start_date', 'is_active']
    list_filter = ['group', 'role', 'is_active']
    search_fields = ['member__first_name', 'member__last_name']



