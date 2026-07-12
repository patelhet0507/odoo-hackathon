from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.contrib import messages
from django.db.models import Q, Prefetch, Count
from django.db.models.functions import TruncDate
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST
from django.utils import timezone
from django.dispatch import receiver
from accounts.decorators import role_required
from accounts.models import User
from .models import Vehicle, Driver, Trip, MaintenanceRecord, FuelLog, Expense, VehicleDocument, AuditLog, Notification, VehicleLocation, Checkpoint
from .forms import (VehicleForm, DriverForm, TripForm, TripCompleteForm,
                    MaintenanceForm, FuelLogForm, ExpenseForm)
import csv, io, json, math, random
from datetime import date, timedelta


def paginate(request, queryset, per_page=20):
    page = int(request.GET.get('page', 1))
    count = queryset.count()
    pages = max(1, (count + per_page - 1) // per_page)
    start = (page - 1) * per_page
    end = start + per_page
    return queryset[start:end], page, pages


def search_queryset(request, queryset, fields):
    q = request.GET.get('q', '').strip()
    if q:
        filters = Q()
        for field in fields:
            filters |= Q(**{f'{field}__icontains': q})
        queryset = queryset.filter(filters)
    return queryset, q


# ---- Vehicle Views ----

@login_required
@role_required(User.Role.FLEET_MANAGER, User.Role.SAFETY_OFFICER, User.Role.FINANCIAL_ANALYST)
def vehicle_list(request):
    qs = Vehicle.objects.prefetch_related(
        Prefetch(
            'trips',
            queryset=Trip.objects.filter(status='Dispatched')
            .select_related('driver').order_by('-created_at')[:1],
            to_attr='active_trip_list',
        ),
        Prefetch(
            'maintenance_records',
            queryset=MaintenanceRecord.objects.order_by('-completed_date', '-scheduled_date')[:1],
            to_attr='recent_maintenance_list',
        ),
    )
    qs, query = search_queryset(request, qs, ['registration_number', 'name', 'model', 'region'])
    type_filter = request.GET.get('type', '')
    status_filter = request.GET.get('status', '')
    if type_filter:
        qs = qs.filter(vehicle_type=type_filter)
    if status_filter:
        qs = qs.filter(status=status_filter)
    vehicles, page, pages = paginate(request, qs)
    page_range = range(1, pages + 1) if pages > 1 else []
    return render(request, 'fleet/vehicle_list.html', {
        'vehicles': vehicles, 'page': page, 'pages': pages, 'page_range': page_range,
        'query': query, 'type_filter': type_filter, 'status_filter': status_filter,
        'vehicle_types': Vehicle.Type.choices, 'vehicle_statuses': Vehicle.Status.choices,
    })


@login_required
@role_required(User.Role.FLEET_MANAGER)
def vehicle_create(request):
    if request.method == 'POST':
        form = VehicleForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Vehicle created successfully.')
            return redirect('fleet:vehicle_list')
    else:
        form = VehicleForm()
    return render(request, 'fleet/vehicle_form.html', {'form': form, 'title': 'Add Vehicle'})


@login_required
@role_required(User.Role.FLEET_MANAGER)
def vehicle_update(request, pk):
    vehicle = get_object_or_404(Vehicle, pk=pk)
    if request.method == 'POST':
        form = VehicleForm(request.POST, instance=vehicle)
        if form.is_valid():
            form.save()
            messages.success(request, 'Vehicle updated successfully.')
            return redirect('fleet:vehicle_list')
    else:
        form = VehicleForm(instance=vehicle)
    return render(request, 'fleet/vehicle_form.html', {'form': form, 'title': 'Edit Vehicle'})


@login_required
@role_required(User.Role.FLEET_MANAGER)
def vehicle_delete(request, pk):
    vehicle = get_object_or_404(Vehicle, pk=pk)
    if request.method == 'POST':
        vehicle.delete()
        messages.success(request, 'Vehicle deleted.')
        return redirect('fleet:vehicle_list')
    return render(request, 'fleet/vehicle_confirm_delete.html', {'object': vehicle})


@login_required
@role_required(User.Role.FLEET_MANAGER, User.Role.SAFETY_OFFICER, User.Role.FINANCIAL_ANALYST)
def vehicle_detail(request, pk):
    vehicle = get_object_or_404(Vehicle, pk=pk)
    trips = vehicle.trips.all()[:10]
    maintenance = vehicle.maintenance_records.all()[:10]
    return render(request, 'fleet/vehicle_detail.html', {
        'vehicle': vehicle, 'trips': trips, 'maintenance': maintenance,
    })


@login_required
@role_required(User.Role.FLEET_MANAGER)
def vehicle_upload_doc(request, pk):
    vehicle = get_object_or_404(Vehicle, pk=pk)
    if request.method == 'POST' and request.FILES.get('file'):
        VehicleDocument.objects.create(
            vehicle=vehicle,
            document_type=request.POST.get('document_type', 'Other'),
            file=request.FILES['file'],
        )
        messages.success(request, 'Document uploaded.')
    return redirect('fleet:vehicle_detail', pk=pk)


@login_required
@role_required(User.Role.FLEET_MANAGER)
def vehicle_delete_doc(request, pk, doc_id):
    doc = get_object_or_404(VehicleDocument, pk=doc_id, vehicle_id=pk)
    doc.file.delete()
    doc.delete()
    messages.success(request, 'Document deleted.')
    return redirect('fleet:vehicle_detail', pk=pk)


# ---- Driver Views ----

@login_required
@role_required(User.Role.FLEET_MANAGER, User.Role.SAFETY_OFFICER)
def driver_list(request):
    qs = Driver.objects.all()
    qs, query = search_queryset(request, qs, ['name', 'license_number', 'contact_number'])
    status_filter = request.GET.get('status', '')
    if status_filter:
        qs = qs.filter(status=status_filter)
    drivers, page, pages = paginate(request, qs)
    return render(request, 'fleet/driver_list.html', {
        'drivers': drivers, 'page': page, 'pages': pages,
        'query': query, 'status_filter': status_filter,
        'driver_statuses': Driver.Status.choices,
    })


@login_required
@role_required(User.Role.FLEET_MANAGER)
def driver_create(request):
    if request.method == 'POST':
        form = DriverForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Driver created successfully.')
            return redirect('fleet:driver_list')
    else:
        form = DriverForm()
    return render(request, 'fleet/driver_form.html', {'form': form, 'title': 'Add Driver'})


@login_required
@role_required(User.Role.FLEET_MANAGER)
def driver_update(request, pk):
    driver = get_object_or_404(Driver, pk=pk)
    if request.method == 'POST':
        form = DriverForm(request.POST, instance=driver)
        if form.is_valid():
            form.save()
            messages.success(request, 'Driver updated successfully.')
            return redirect('fleet:driver_list')
    else:
        form = DriverForm(instance=driver)
    return render(request, 'fleet/driver_form.html', {'form': form, 'title': 'Edit Driver'})


@login_required
@role_required(User.Role.FLEET_MANAGER)
def driver_delete(request, pk):
    driver = get_object_or_404(Driver, pk=pk)
    if request.method == 'POST':
        driver.delete()
        messages.success(request, 'Driver deleted.')
        return redirect('fleet:driver_list')
    return render(request, 'fleet/driver_confirm_delete.html', {'object': driver})


@login_required
@role_required(User.Role.FLEET_MANAGER, User.Role.SAFETY_OFFICER)
def driver_detail(request, pk):
    driver = get_object_or_404(Driver, pk=pk)
    trips = driver.trips.all()[:10]
    return render(request, 'fleet/driver_detail.html', {'driver': driver, 'trips': trips})


# ---- Trip Views ----

@login_required
def trip_list(request):
    if request.user.role == User.Role.DRIVER and hasattr(request.user, 'driver_profile') and request.user.driver_profile:
        qs = Trip.objects.select_related('vehicle', 'driver').filter(driver=request.user.driver_profile)
    else:
        qs = Trip.objects.select_related('vehicle', 'driver').all()
    qs, query = search_queryset(request, qs, ['source', 'destination'])
    status_filter = request.GET.get('status', '')
    if status_filter:
        qs = qs.filter(status=status_filter)
    trips, page, pages = paginate(request, qs)
    return render(request, 'fleet/trip_list.html', {
        'trips': trips, 'page': page, 'pages': pages,
        'query': query, 'status_filter': status_filter,
        'trip_statuses': Trip.Status.choices,
    })


@login_required
@role_required(User.Role.FLEET_MANAGER)
def trip_create(request):
    if request.method == 'POST':
        form = TripForm(request.POST)
        if form.is_valid():
            trip = form.save()
            messages.success(request, 'Trip created as Draft.')
            return redirect('fleet:trip_list')
    else:
        form = TripForm()
    return render(request, 'fleet/trip_form.html', {'form': form, 'title': 'Create Trip'})


@login_required
@role_required(User.Role.FLEET_MANAGER)
def trip_dispatch(request, pk):
    trip = get_object_or_404(Trip, pk=pk)
    if trip.status != Trip.Status.DRAFT:
        messages.error(request, 'Only Draft trips can be dispatched.')
        return redirect('fleet:trip_list')
    trip.status = Trip.Status.DISPATCHED
    trip.start_odometer = trip.vehicle.odometer
    trip.save()
    messages.success(request, f'Trip #{trip.id} dispatched.')
    return redirect('fleet:trip_list')


@login_required
def trip_complete(request, pk):
    trip = get_object_or_404(Trip, pk=pk)
    if request.user.role == User.Role.DRIVER:
        if not hasattr(request.user, 'driver_profile') or not request.user.driver_profile or trip.driver != request.user.driver_profile:
            messages.error(request, 'You can only complete your own trips.')
            return redirect('fleet:trip_list')
    if trip.status != Trip.Status.DISPATCHED:
        messages.error(request, 'Only Dispatched trips can be completed.')
        return redirect('fleet:trip_list')
    if request.method == 'POST':
        form = TripCompleteForm(request.POST, instance=trip)
        if form.is_valid():
            trip = form.save(commit=False)
            trip.status = Trip.Status.COMPLETED
            trip.save()
            messages.success(request, f'Trip #{trip.id} completed.')
            return redirect('fleet:trip_list')
    else:
        form = TripCompleteForm(instance=trip)
    return render(request, 'fleet/trip_complete.html', {'form': form, 'trip': trip})


@login_required
@role_required(User.Role.FLEET_MANAGER)
def trip_cancel(request, pk):
    trip = get_object_or_404(Trip, pk=pk)
    if trip.status not in (Trip.Status.DRAFT, Trip.Status.DISPATCHED):
        messages.error(request, 'Trip cannot be cancelled.')
        return redirect('fleet:trip_list')
    trip.status = Trip.Status.CANCELLED
    trip.save()
    messages.success(request, f'Trip #{trip.id} cancelled.')
    return redirect('fleet:trip_list')


@login_required
def trip_detail(request, pk):
    trip = get_object_or_404(Trip.objects.select_related('vehicle', 'driver'), pk=pk)
    if request.user.role == User.Role.DRIVER:
        if not hasattr(request.user, 'driver_profile') or not request.user.driver_profile or trip.driver != request.user.driver_profile:
            messages.error(request, 'You can only view your own trips.')
            return redirect('fleet:trip_list')
    return render(request, 'fleet/trip_detail.html', {'trip': trip})


# ---- Maintenance Views ----

@login_required
@role_required(User.Role.FLEET_MANAGER, User.Role.SAFETY_OFFICER)
def maintenance_list(request):
    qs = MaintenanceRecord.objects.select_related('vehicle').all()
    qs, query = search_queryset(request, qs, ['description', 'maintenance_type', 'vehicle__registration_number'])
    status_filter = request.GET.get('status', '')
    if status_filter:
        qs = qs.filter(status=status_filter)
    records, page, pages = paginate(request, qs)
    return render(request, 'fleet/maintenance_list.html', {
        'records': records, 'page': page, 'pages': pages,
        'query': query, 'status_filter': status_filter,
    })


@login_required
@role_required(User.Role.FLEET_MANAGER, User.Role.SAFETY_OFFICER)
def maintenance_create(request):
    if request.method == 'POST':
        form = MaintenanceForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Maintenance record created. Vehicle is now In Shop.')
            return redirect('fleet:maintenance_list')
    else:
        form = MaintenanceForm()
    return render(request, 'fleet/maintenance_form.html', {'form': form, 'title': 'Add Maintenance'})


@login_required
@role_required(User.Role.FLEET_MANAGER, User.Role.SAFETY_OFFICER)
def maintenance_close(request, pk):
    record = get_object_or_404(MaintenanceRecord, pk=pk)
    if record.status != MaintenanceRecord.Status.OPEN:
        messages.error(request, 'Maintenance record is already closed.')
        return redirect('fleet:maintenance_list')
    record.status = MaintenanceRecord.Status.CLOSED
    record.save()
    messages.success(request, 'Maintenance closed. Vehicle is now Available.')
    return redirect('fleet:maintenance_list')


# ---- Fuel & Expense Views ----

@login_required
@role_required(User.Role.FLEET_MANAGER, User.Role.FINANCIAL_ANALYST)
def fuel_list(request):
    qs = FuelLog.objects.select_related('vehicle').all()
    qs, query = search_queryset(request, qs, ['vehicle__registration_number'])
    fuels, page, pages = paginate(request, qs)
    return render(request, 'fleet/fuel_list.html', {
        'fuels': fuels, 'page': page, 'pages': pages, 'query': query,
    })


@login_required
@role_required(User.Role.FLEET_MANAGER, User.Role.FINANCIAL_ANALYST)
def fuel_create(request):
    if request.method == 'POST':
        form = FuelLogForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Fuel log recorded.')
            return redirect('fleet:fuel_list')
    else:
        form = FuelLogForm()
    return render(request, 'fleet/fuel_form.html', {'form': form, 'title': 'Record Fuel'})


@login_required
@role_required(User.Role.FLEET_MANAGER, User.Role.FINANCIAL_ANALYST)
def expense_list(request):
    qs = Expense.objects.select_related('vehicle').all()
    qs, query = search_queryset(request, qs, ['vehicle__registration_number', 'expense_type', 'description'])
    expenses, page, pages = paginate(request, qs)
    return render(request, 'fleet/expense_list.html', {
        'expenses': expenses, 'page': page, 'pages': pages, 'query': query,
    })


@login_required
@role_required(User.Role.FLEET_MANAGER, User.Role.FINANCIAL_ANALYST)
def expense_create(request):
    if request.method == 'POST':
        form = ExpenseForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Expense recorded.')
            return redirect('fleet:expense_list')
    else:
        form = ExpenseForm()
    return render(request, 'fleet/expense_form.html', {'form': form, 'title': 'Record Expense'})


# ============================================================
# AUDIT LOGS
# ============================================================

@login_required
@role_required(User.Role.FLEET_MANAGER)
def audit_log_list(request):
    qs = AuditLog.objects.select_related('user').all()
    qs, query = search_queryset(request, qs, ['username', 'action', 'module', 'object_repr'])
    action_filter = request.GET.get('action', '')
    module_filter = request.GET.get('module', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    if action_filter:
        qs = qs.filter(action=action_filter)
    if module_filter:
        qs = qs.filter(module=module_filter)
    if date_from:
        qs = qs.filter(created_at__date__gte=date_from)
    if date_to:
        qs = qs.filter(created_at__date__lte=date_to)
    logs, page, pages = paginate(request, qs, per_page=25)
    page_range = range(1, pages + 1) if pages > 1 else []
    actions = AuditLog.objects.values_list('action', flat=True).distinct().order_by('action')
    modules = AuditLog.objects.values_list('module', flat=True).distinct().order_by('module')

    if 'export' in request.GET:
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="audit_logs.csv"'
        writer = csv.writer(response)
        writer.writerow(['Timestamp', 'Username', 'Role', 'Action', 'Module', 'Object', 'Previous Value', 'New Value', 'IP Address'])
        for log in qs:
            writer.writerow([log.created_at, log.username, log.role, log.action, log.module,
                           log.object_repr, log.previous_value, log.new_value, log.ip_address])
        return response

    return render(request, 'fleet/audit_log_list.html', {
        'logs': logs, 'page': page, 'pages': pages, 'page_range': page_range,
        'query': query, 'action_filter': action_filter, 'module_filter': module_filter,
        'date_from': date_from, 'date_to': date_to, 'actions': actions, 'modules': modules,
    })


# ============================================================
# NOTIFICATIONS
# ============================================================

@login_required
def notification_list(request):
    qs = Notification.objects.filter(user=request.user)
    type_filter = request.GET.get('type', '')
    read_filter = request.GET.get('read', '')
    if type_filter:
        qs = qs.filter(notification_type=type_filter)
    if read_filter == 'read':
        qs = qs.filter(is_read=True)
    elif read_filter == 'unread':
        qs = qs.filter(is_read=False)
    notifications, page, pages = paginate(request, qs, per_page=20)
    page_range = range(1, pages + 1) if pages > 1 else []
    return render(request, 'fleet/notification_list.html', {
        'notifications': notifications, 'page': page, 'pages': pages, 'page_range': page_range,
        'type_filter': type_filter, 'read_filter': read_filter,
        'notification_types': Notification.Type.choices,
    })


@login_required
@require_POST
def notification_mark_read(request, pk):
    notification = get_object_or_404(Notification, pk=pk, user=request.user)
    notification.is_read = True
    notification.save()
    return JsonResponse({'status': 'ok'})


@login_required
@require_POST
def notification_mark_all_read(request):
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    return JsonResponse({'status': 'ok'})


@login_required
@require_POST
def notification_delete(request, pk):
    notification = get_object_or_404(Notification, pk=pk, user=request.user)
    notification.delete()
    return JsonResponse({'status': 'ok'})


@login_required
def notification_unread_count(request):
    count = Notification.objects.filter(user=request.user, is_read=False).count()
    return JsonResponse({'count': count})


# ============================================================
# LIVE VEHICLE TRACKING
# ============================================================

@login_required
@role_required(User.Role.FLEET_MANAGER, User.Role.SAFETY_OFFICER, User.Role.FINANCIAL_ANALYST)
def live_tracking(request):
    active_trips = Trip.objects.select_related('vehicle', 'driver').filter(
        status=Trip.Status.DISPATCHED
    )
    return render(request, 'fleet/live_tracking.html', {
        'active_trips': active_trips,
    })


CITIES = {
    'Mumbai': (19.0760, 72.8777),
    'Delhi': (28.7041, 77.1025),
    'Bangalore': (12.9716, 77.5946),
    'Chennai': (13.0827, 80.2707),
    'Hyderabad': (17.3850, 78.4867),
    'Pune': (18.5204, 73.8567),
    'Ahmedabad': (23.0225, 72.5714),
    'Kolkata': (22.5726, 88.3639),
    'Jaipur': (26.9124, 75.7873),
    'Lucknow': (26.8467, 80.9462),
}


@login_required
def vehicle_locations_json(request):
    vehicles = Vehicle.objects.filter(status=Vehicle.Status.ON_TRIP)
    data = []
    for v in vehicles:
        latest = v.locations.filter(is_active=True).first()
        if not latest:
            lat, lng = CITIES.get(v.region, (19.0760, 72.8777))
            lon_off = (hash(v.pk) % 100) / 1000.0
            lat_off = (hash(v.pk + 1000) % 100) / 1000.0
            lat, lng = lat + lat_off, lng + lon_off
            latest = VehicleLocation.objects.create(vehicle=v, latitude=lat, longitude=lng, speed=0, heading=0, is_active=True)
        trip = v.active_trip
        if trip:
            data.append({
                'id': v.id,
                'registration': v.registration_number,
                'name': v.name,
                'lat': float(latest.latitude),
                'lng': float(latest.longitude),
                'speed': float(latest.speed),
                'heading': latest.heading,
                'status': v.status,
                'driver': trip.driver.name if trip.driver else 'Unknown',
                'source': trip.source,
                'destination': trip.destination,
            })
    return JsonResponse({'vehicles': data})


@login_required
def vehicle_route_json(request, pk):
    trip = get_object_or_404(Trip, pk=pk)
    checkpoints = trip.checkpoints.all()
    route = [{'lat': float(c.latitude), 'lng': float(c.longitude)} for c in checkpoints if c.latitude and c.longitude]
    latest = trip.vehicle.locations.filter(is_active=True).first()
    current = {'lat': float(latest.latitude), 'lng': float(latest.longitude)} if latest else None
    return JsonResponse({'route': route, 'current': current, 'source': trip.source, 'destination': trip.destination})


@login_required
def simulate_location(request):
    if request.user.role != User.Role.FLEET_MANAGER:
        return JsonResponse({'error': 'Not authorized'}, status=403)
    for v in Vehicle.objects.filter(status=Vehicle.Status.ON_TRIP):
        old = v.locations.filter(is_active=True).first()
        base_lat = float(old.latitude) if old else 19.0760
        base_lng = float(old.longitude) if old else 72.8777
        lat = base_lat + random.uniform(-0.005, 0.005)
        lng = base_lng + random.uniform(-0.005, 0.005)
        speed = random.uniform(20, 80)
        heading = random.randint(0, 359)
        VehicleLocation.objects.create(
            vehicle=v, latitude=lat, longitude=lng,
            speed=speed, heading=heading, is_active=True,
        )
    VehicleLocation.objects.filter(is_active=True).exclude(
        id__in=VehicleLocation.objects.filter(is_active=True).values('vehicle_id').annotate(
            max_id=Count('id')
        ).values('max_id')
    ).update(is_active=False)
    return JsonResponse({'status': 'ok'})



# ============================================================
# TRIP TIMELINE & ROUTE HISTORY
# ============================================================

@login_required
def trip_timeline(request, pk):
    trip = get_object_or_404(Trip.objects.select_related('vehicle', 'driver'), pk=pk)
    if request.user.role == User.Role.DRIVER:
        if not hasattr(request.user, 'driver_profile') or not request.user.driver_profile or trip.driver != request.user.driver_profile:
            messages.error(request, 'You can only view your own trip timelines.')
            return redirect('fleet:trip_list')
    if trip.status not in (Trip.Status.DISPATCHED, Trip.Status.COMPLETED):
        messages.error(request, 'Timeline is only available for dispatched or completed trips.')
        return redirect('fleet:trip_detail', pk=pk)
    checkpoints = trip.checkpoints.all()
    latest = trip.vehicle.locations.filter(is_active=True).first()
    return render(request, 'fleet/trip_timeline.html', {
        'trip': trip, 'checkpoints': checkpoints, 'latest': latest,
    })
