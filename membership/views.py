from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Section, Position, Member, Dependent, PositionHistory, MemberTransfer
from .serializers import (
    SectionSerializer, PositionSerializer, MemberSerializer, MemberListSerializer,
    DependentSerializer, PositionHistorySerializer, MemberTransferSerializer
)


class SectionViewSet(viewsets.ModelViewSet):
    queryset = Section.objects.all()
    serializer_class = SectionSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']


class PositionViewSet(viewsets.ModelViewSet):
    queryset = Position.objects.all()
    serializer_class = PositionSerializer
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['title']
    filterset_fields = ['level']


class MemberViewSet(viewsets.ModelViewSet):
    queryset = Member.objects.select_related('section').prefetch_related('current_positions', 'dependents', 'position_history')
    filter_backends = [filters.SearchFilter, DjangoFilterBackend, filters.OrderingFilter]
    search_fields = ['first_name', 'last_name', 'email', 'phone']
    filterset_fields = ['gender', 'membership_status', 'section', 'current_positions', 'transfer_type']
    ordering_fields = ['last_name', 'date_joined', 'date_of_birth']
    ordering = ['last_name']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return MemberListSerializer
        return MemberSerializer
    
    @action(detail=False, methods=['post'])
    def import_csv(self, request):
        """Import members from CSV file"""
        import csv
        import io
        from datetime import datetime
        
        file = request.FILES.get('file')
        if not file:
            return Response({'error': 'No file provided'}, status=400)
            
        try:
            decoded_file = file.read().decode('utf-8')
            io_string = io.StringIO(decoded_file)
            reader = csv.DictReader(io_string)
            
            imported_count = 0
            errors = []
            
            for index, row in enumerate(reader):
                try:
                    # Basic fields
                    member_data = {
                        'first_name': row.get('First Name'),
                        'last_name': row.get('Last Name'),
                        'middle_name': row.get('Middle Name', ''),
                        'gender': row.get('Gender', 'M'),
                        'phone': row.get('Phone', ''),
                        'email': row.get('Email', ''),
                        'address': row.get('Address', ''),
                        'membership_status': row.get('Status', 'communicant').lower(),
                        'date_of_birth': row.get('Date of Birth'),
                        'date_joined': row.get('Date Joined'),
                    }
                    
                    # Handle Dates
                    for date_field in ['date_of_birth', 'date_joined']:
                        if member_data.get(date_field):
                            try:
                                member_data[date_field] = datetime.strptime(member_data[date_field], '%Y-%m-%d').date()
                            except ValueError:
                                # Try alternative format
                                try:
                                    member_data[date_field] = datetime.strptime(member_data[date_field], '%d/%m/%Y').date()
                                except ValueError:
                                    member_data[date_field] = datetime.now().date() # Fallback
                        else:
                            member_data[date_field] = datetime.now().date() # Default
                            
                    # Handle Section
                    section_name = row.get('Section')
                    if section_name:
                        section, _ = Section.objects.get_or_create(name=section_name)
                        member_data['section'] = section
                        
                    member = Member.objects.create(**member_data)
                    
                    # Handle Positions
                    positions_str = row.get('Position')
                    if positions_str:
                        for pos_title in positions_str.split(';'):
                            pos_title = pos_title.strip()
                            if pos_title:
                                position, _ = Position.objects.get_or_create(title=pos_title, defaults={'level': 'congregation'})
                                member.current_positions.add(position)
                    
                    # Handle Dependents
                    dependents_str = row.get('Dependents')
                    if dependents_str:
                        for dep_entry in dependents_str.split(';'):
                            if not dep_entry.strip():
                                continue
                            
                            try:
                                parts = [p.strip() for p in dep_entry.split('|')]
                                if len(parts) >= 1:
                                    full_name = parts[0]
                                    gender = parts[1] if len(parts) > 1 else 'M'
                                    dob_str = parts[2] if len(parts) > 2 else None
                                    
                                    # Split name
                                    name_parts = full_name.split()
                                    first_name = name_parts[0]
                                    last_name = " ".join(name_parts[1:]) if len(name_parts) > 1 else member.last_name
                                    
                                    dep_data = {
                                        'principal_member': member,
                                        'first_name': first_name,
                                        'last_name': last_name,
                                        'gender': gender,
                                    }
                                    
                                    if dob_str:
                                        try:
                                            dep_data['date_of_birth'] = datetime.strptime(dob_str, '%Y-%m-%d').date()
                                        except ValueError:
                                            try:
                                                dep_data['date_of_birth'] = datetime.strptime(dob_str, '%d/%m/%Y').date()
                                            except ValueError:
                                                dep_data['date_of_birth'] = datetime.now().date()
                                    else:
                                        dep_data['date_of_birth'] = datetime.now().date()
                                        
                                    Dependent.objects.create(**dep_data)
                            except Exception as dep_e:
                                errors.append(f"Row {index + 1} (Dependent): {str(dep_e)}")

                    imported_count += 1
                    
                except Exception as e:
                    errors.append(f"Row {index + 1}: {str(e)}")
                    
            return Response({
                'status': 'Import complete',
                'imported': imported_count,
                'errors': errors
            })
            
        except Exception as e:
            return Response({'error': str(e)}, status=400)

    @action(detail=True, methods=['post'])
    def add_dependent(self, request, pk=None):
        """Add a dependent to a member"""
        member = self.get_object()
        serializer = DependentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(principal_member=member)
            return Response(serializer.data)
        return Response(serializer.errors, status=400)
    
    @action(detail=True, methods=['post'])
    def change_position(self, request, pk=None):
        """Change member's positions and record history"""
        member = self.get_object()
        position_ids = request.data.get('position_ids', []) # Expected list of IDs
        start_date = request.data.get('start_date')
        
        if not position_ids or not start_date:
            return Response({'error': 'position_ids and start_date are required'}, status=400)
        
        # Close all current position histories
        PositionHistory.objects.filter(
            member=member,
            end_date__isnull=True
        ).update(end_date=start_date)
        
        # Clear current positions and add new ones
        new_positions = Position.objects.filter(id__in=position_ids)
        member.current_positions.set(new_positions)
        
        # Create new position histories
        for position in new_positions:
            PositionHistory.objects.create(
                member=member,
                position=position,
                start_date=start_date
            )
        
        return Response({'status': 'Positions updated successfully'})


class DependentViewSet(viewsets.ModelViewSet):
    queryset = Dependent.objects.select_related('principal_member')
    serializer_class = DependentSerializer
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['first_name', 'last_name']
    filterset_fields = ['gender', 'membership_status', 'principal_member']


class PositionHistoryViewSet(viewsets.ModelViewSet):
    queryset = PositionHistory.objects.select_related('member', 'position')
    serializer_class = PositionHistorySerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['member', 'position']


class MemberTransferViewSet(viewsets.ModelViewSet):
    queryset = MemberTransfer.objects.select_related('member')
    serializer_class = MemberTransferSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['transfer_type', 'approval_status', 'member']
    
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Approve a transfer"""
        transfer = self.get_object()
        transfer.approval_status = 'approved'
        transfer.save()
        return Response({'status': 'Transfer approved'})
    
    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        """Reject a transfer"""
        transfer = self.get_object()
        transfer.approval_status = 'rejected'
        transfer.save()
        return Response({'status': 'Transfer rejected'})
