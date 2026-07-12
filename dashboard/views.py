from datetime import date, timedelta
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count, Q
from accounts.models import User
from fleet.models import Vehicle, Driver, Trip, MaintenanceRecord, FuelLog, Expense


@login_required
def home(request):
    role = request.user.role
    context = {'user_role': role}

    if role == User.Role.DRIVER:
        driver = getattr(request.user, 'driver_profile', None)
        if driver:
            my_trips = Trip.objects.filter(driver=driver)
            context.update({
                'my_active_trips': my_trips.filter(status=Trip.Status.DISPATCHED).count(),
                'my_completed_trips': my_trips.filter(status=Trip.Status.COMPLETED).count(),
                'my_pending_trips': my_trips.filter(status=Trip.Status.DRAFT).count(),
                'my_total_trips': my_trips.count(),
                'recent_trips': my_trips.select_related('vehicle').order_by('-created_at')[:5],
                'total_vehicles': Vehicle.objects.count(),
                'total_drivers': Driver.objects.count(),
                'open_maintenance': MaintenanceRecord.objects.filter(status=MaintenanceRecord.Status.OPEN).count(),
                'vehicle_types': Vehicle.Type.choices,
                'vehicle_statuses': Vehicle.Status.choices,
            })
        else:
            context.update({
                'my_active_trips': 0, 'my_completed_trips': 0,
                'my_pending_trips': 0, 'my_total_trips': 0,
                'recent_trips': [], 'total_vehicles': 0, 'total_drivers': 0,
                'open_maintenance': 0, 'vehicle_types': [], 'vehicle_statuses': [],
            })
        return render(request, 'dashboard/home.html', context)

    vehicle_stats = Vehicle.objects.aggregate(
        total=Count('id'),
        active=Count('id', filter=Q(status=Vehicle.Status.ON_TRIP)),
        available=Count('id', filter=Q(status=Vehicle.Status.AVAILABLE)),
        in_shop=Count('id', filter=Q(status=Vehicle.Status.IN_SHOP)),
        retired=Count('id', filter=Q(status=Vehicle.Status.RETIRED)),
    )
    driver_stats = Driver.objects.aggregate(
        total=Count('id'),
        on_duty=Count('id', filter=Q(status=Driver.Status.ON_TRIP)),
        available=Count('id', filter=Q(status=Driver.Status.AVAILABLE)),
        off_duty=Count('id', filter=Q(status=Driver.Status.OFF_DUTY)),
        suspended=Count('id', filter=Q(status=Driver.Status.SUSPENDED)),
        expired=Count('id', filter=Q(license_expiry_date__lt=date.today())),
    )
    trip_stats = Trip.objects.aggregate(
        active=Count('id', filter=Q(status=Trip.Status.DISPATCHED)),
        pending=Count('id', filter=Q(status=Trip.Status.DRAFT)),
        completed=Count('id', filter=Q(status=Trip.Status.COMPLETED)),
        cancelled=Count('id', filter=Q(status=Trip.Status.CANCELLED)),
    )
    open_maintenance = MaintenanceRecord.objects.filter(status=MaintenanceRecord.Status.OPEN).count()

    total_vehicles = vehicle_stats['total']
    active_vehicles = vehicle_stats['active']
    fleet_utilization = round((active_vehicles / total_vehicles * 100), 1) if total_vehicles else 0

    total_fuel_cost = FuelLog.objects.aggregate(total=Sum('cost'))['total'] or 0
    total_maint_cost = MaintenanceRecord.objects.aggregate(total=Sum('cost'))['total'] or 0
    total_expense_amount = Expense.objects.aggregate(total=Sum('amount'))['total'] or 0
    total_operational_cost = float(total_fuel_cost) + float(total_maint_cost) + float(total_expense_amount)

    today = date.today()
    week_ago = today - timedelta(days=7)
    trips_this_week = Trip.objects.filter(created_at__date__gte=week_ago).count()
    upcoming_maintenance = MaintenanceRecord.objects.filter(
        status=MaintenanceRecord.Status.OPEN,
        scheduled_date__gte=today,
    ).count()
    overdue_maintenance = MaintenanceRecord.objects.filter(
        status=MaintenanceRecord.Status.OPEN,
        scheduled_date__lt=today,
    ).count()

    recent_trips = Trip.objects.select_related('vehicle', 'driver').filter(
        status__in=[Trip.Status.DISPATCHED, Trip.Status.COMPLETED]
    ).order_by('-created_at')[:5]

    region_data = Vehicle.objects.values('region').annotate(count=Count('id')).order_by('-count')
    type_data = Vehicle.objects.values('vehicle_type').annotate(count=Count('id')).order_by('-count')

    vehicle_type_filter = request.GET.get('type', '')
    status_filter = request.GET.get('status', '')
    region_filter = request.GET.get('region', '')

    context.update({
        'total_vehicles': total_vehicles,
        'active_vehicles': active_vehicles,
        'available_vehicles': vehicle_stats['available'],
        'in_shop_vehicles': vehicle_stats['in_shop'],
        'retired_vehicles': vehicle_stats['retired'],
        'total_drivers': driver_stats['total'],
        'drivers_on_duty': driver_stats['on_duty'],
        'drivers_available': driver_stats['available'],
        'drivers_off_duty': driver_stats['off_duty'],
        'drivers_suspended': driver_stats['suspended'],
        'expired_licenses': driver_stats['expired'],
        'active_trips': trip_stats['active'],
        'pending_trips': trip_stats['pending'],
        'completed_trips': trip_stats['completed'],
        'cancelled_trips': trip_stats['cancelled'],
        'open_maintenance': open_maintenance,
        'fleet_utilization': fleet_utilization,
        'total_fuel_cost': total_fuel_cost,
        'total_maint_cost': total_maint_cost,
        'total_operational_cost': total_operational_cost,
        'trips_this_week': trips_this_week,
        'upcoming_maintenance': upcoming_maintenance,
        'overdue_maintenance': overdue_maintenance,
        'recent_trips': recent_trips,
        'region_data': region_data,
        'type_data': type_data,
        'vehicle_types': Vehicle.Type.choices,
        'vehicle_statuses': Vehicle.Status.choices,
        'vehicle_type_filter': vehicle_type_filter,
        'status_filter': status_filter,
        'region_filter': region_filter,
    })
    return render(request, 'dashboard/home.html', context)
