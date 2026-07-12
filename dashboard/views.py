from datetime import date
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from fleet.models import Vehicle, Driver, Trip, MaintenanceRecord


@login_required
def home(request):
    total_vehicles = Vehicle.objects.count()
    active_vehicles = Vehicle.objects.filter(status=Vehicle.Status.ON_TRIP).count()
    available_vehicles = Vehicle.objects.filter(status=Vehicle.Status.AVAILABLE).count()
    in_shop_vehicles = Vehicle.objects.filter(status=Vehicle.Status.IN_SHOP).count()
    retired_vehicles = Vehicle.objects.filter(status=Vehicle.Status.RETIRED).count()

    total_drivers = Driver.objects.count()
    drivers_on_duty = Driver.objects.filter(status=Driver.Status.ON_TRIP).count()
    drivers_available = Driver.objects.filter(status=Driver.Status.AVAILABLE).count()
    drivers_off_duty = Driver.objects.filter(status=Driver.Status.OFF_DUTY).count()
    drivers_suspended = Driver.objects.filter(status=Driver.Status.SUSPENDED).count()
    expired_licenses = Driver.objects.filter(license_expiry_date__lt=date.today()).count()

    active_trips = Trip.objects.filter(status=Trip.Status.DISPATCHED).count()
    pending_trips = Trip.objects.filter(status=Trip.Status.DRAFT).count()
    completed_trips = Trip.objects.filter(status=Trip.Status.COMPLETED).count()
    cancelled_trips = Trip.objects.filter(status=Trip.Status.CANCELLED).count()

    open_maintenance = MaintenanceRecord.objects.filter(status=MaintenanceRecord.Status.OPEN).count()

    fleet_utilization = 0
    if total_vehicles > 0:
        fleet_utilization = round((active_vehicles / total_vehicles) * 100, 1)

    context = {
        'total_vehicles': total_vehicles,
        'active_vehicles': active_vehicles,
        'available_vehicles': available_vehicles,
        'in_shop_vehicles': in_shop_vehicles,
        'retired_vehicles': retired_vehicles,
        'total_drivers': total_drivers,
        'drivers_on_duty': drivers_on_duty,
        'drivers_available': drivers_available,
        'drivers_off_duty': drivers_off_duty,
        'drivers_suspended': drivers_suspended,
        'expired_licenses': expired_licenses,
        'active_trips': active_trips,
        'pending_trips': pending_trips,
        'completed_trips': completed_trips,
        'cancelled_trips': cancelled_trips,
        'open_maintenance': open_maintenance,
        'fleet_utilization': fleet_utilization,
        'vehicle_types': Vehicle.Type.choices,
        'vehicle_statuses': Vehicle.Status.choices,
    }
    return render(request, 'dashboard/home.html', context)


