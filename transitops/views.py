from django.shortcuts import render
from django.http import HttpResponse
from django.core.management import call_command
from io import StringIO
from fleet.models import Vehicle, Driver, Trip


def landing(request):
    veh_count = Vehicle.objects.count()
    drv_count = Driver.objects.count()
    trip_count = Trip.objects.count()
    return render(request, 'landing.html', {
        'vehicle_count': veh_count,
        'driver_count': drv_count,
        'trip_count': trip_count,
    })


def cron_check_licenses(request):
    token = request.GET.get('token', '')
    if token != 'transitops-cron-secret':
        return HttpResponse('Forbidden', status=403)
    out = StringIO()
    call_command('check_licenses', stdout=out)
    return HttpResponse(out.getvalue())
