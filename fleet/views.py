from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Prefetch
from django.views.decorators.cache import cache_page
from .models import Vehicle, Driver, Trip, MaintenanceRecord, FuelLog, Expense, VehicleDocument
from .forms import (VehicleForm, DriverForm, TripForm, TripCompleteForm,
                    MaintenanceForm, FuelLogForm, ExpenseForm)


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
def vehicle_list(request):
    # ponytail: 2 prefetches replace 9 correlated subqueries (was 9N hits, now ~2)
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
def vehicle_delete(request, pk):
    vehicle = get_object_or_404(Vehicle, pk=pk)
    if request.method == 'POST':
        vehicle.delete()
        messages.success(request, 'Vehicle deleted.')
        return redirect('fleet:vehicle_list')
    return render(request, 'fleet/vehicle_confirm_delete.html', {'object': vehicle})


@login_required
def vehicle_detail(request, pk):
    vehicle = get_object_or_404(Vehicle, pk=pk)
    trips = vehicle.trips.all()[:10]
    maintenance = vehicle.maintenance_records.all()[:10]
    return render(request, 'fleet/vehicle_detail.html', {
        'vehicle': vehicle, 'trips': trips, 'maintenance': maintenance,
    })


# ---- Driver Views ----

@login_required
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
def driver_delete(request, pk):
    driver = get_object_or_404(Driver, pk=pk)
    if request.method == 'POST':
        driver.delete()
        messages.success(request, 'Driver deleted.')
        return redirect('fleet:driver_list')
    return render(request, 'fleet/driver_confirm_delete.html', {'object': driver})


@login_required
def driver_detail(request, pk):
    driver = get_object_or_404(Driver, pk=pk)
    trips = driver.trips.all()[:10]
    return render(request, 'fleet/driver_detail.html', {'driver': driver, 'trips': trips})


# ---- Trip Views ----

@login_required
def trip_list(request):
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
    return render(request, 'fleet/trip_detail.html', {'trip': trip})


# ---- Maintenance Views ----

@login_required
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
def fuel_list(request):
    qs = FuelLog.objects.select_related('vehicle').all()
    qs, query = search_queryset(request, qs, ['vehicle__registration_number'])
    fuels, page, pages = paginate(request, qs)
    return render(request, 'fleet/fuel_list.html', {
        'fuels': fuels, 'page': page, 'pages': pages, 'query': query,
    })


@login_required
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
def expense_list(request):
    qs = Expense.objects.select_related('vehicle').all()
    qs, query = search_queryset(request, qs, ['vehicle__registration_number', 'expense_type', 'description'])
    expenses, page, pages = paginate(request, qs)
    return render(request, 'fleet/expense_list.html', {
        'expenses': expenses, 'page': page, 'pages': pages, 'query': query,
    })


@login_required
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


@login_required
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
def vehicle_delete_doc(request, pk, doc_id):
    doc = get_object_or_404(VehicleDocument, pk=doc_id, vehicle_id=pk)
    doc.file.delete()
    doc.delete()
    messages.success(request, 'Document deleted.')
    return redirect('fleet:vehicle_detail', pk=pk)


