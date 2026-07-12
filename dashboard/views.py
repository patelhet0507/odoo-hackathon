from datetime import date
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_page
from django.db.models import Count, Q
from fleet.models import Vehicle, Driver, Trip, MaintenanceRecord


@login_required
@cache_page(60)
def home(request):
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

    context = {
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
        'vehicle_types': Vehicle.Type.choices,
        'vehicle_statuses': Vehicle.Status.choices,
    }
    return render(request, 'dashboard/home.html', context)
