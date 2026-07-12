import os, csv, io
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_page
from django.db.models import Sum, Subquery, OuterRef
from django.http import HttpResponse
from django.template.loader import get_template
from django.conf import settings
from fleet.models import Vehicle, Trip, FuelLog, MaintenanceRecord, Expense

try:
    from xhtml2pdf import pisa
    HAS_XHTML2PDF = True
except ImportError:
    HAS_XHTML2PDF = False


@login_required
@cache_page(120)
def analytics(request):
    total = Vehicle.objects.count()
    active_veh = Vehicle.objects.filter(status=Vehicle.Status.ON_TRIP).count()
    fleet_util = round((active_veh / total * 100), 1) if total else 0

    trip_stats = Trip.objects.filter(status=Trip.Status.COMPLETED).aggregate(
        total_distance=Sum('actual_distance'),
        total_fuel=Sum('fuel_consumed'),
    )
    total_distance = trip_stats['total_distance'] or 0
    total_fuel = trip_stats['total_fuel'] or 0
    fuel_efficiency = round(float(total_distance) / float(total_fuel), 2) if total_fuel else 0

    fuel_cost = FuelLog.objects.aggregate(total=Sum('cost'))['total'] or 0
    maint_cost = MaintenanceRecord.objects.aggregate(total=Sum('cost'))['total'] or 0
    other_cost = Expense.objects.aggregate(total=Sum('amount'))['total'] or 0
    total_op_cost = float(fuel_cost) + float(maint_cost) + float(other_cost)

    # ponytail: two dict lookups instead of N aggregate queries per vehicle
    maint_by_vehicle = dict(
        MaintenanceRecord.objects.values_list('vehicle_id')
        .annotate(total=Sum('cost'))
        .values_list('vehicle_id', 'total')
    )
    fuel_by_vehicle = dict(
        FuelLog.objects.values_list('vehicle_id')
        .annotate(total=Sum('cost'))
        .values_list('vehicle_id', 'total')
    )

    vehicle_rois = []
    for v in Vehicle.objects.all():
        maint = float(maint_by_vehicle.get(v.pk, 0) or 0)
        fuel = float(fuel_by_vehicle.get(v.pk, 0) or 0)
        total_exp = maint + fuel
        acq = float(v.acquisition_cost)
        roi = round(((0 - total_exp) / acq) * 100, 1) if acq else 0
        vehicle_rois.append({
            'vehicle': str(v),
            'acquisition_cost': acq,
            'maintenance_cost': maint,
            'fuel_cost': fuel,
            'total_cost': total_exp,
            'roi': roi,
        })

    completed = Trip.objects.filter(status=Trip.Status.COMPLETED).count()
    cancelled = Trip.objects.filter(status=Trip.Status.CANCELLED).count()

    context = {
        'fleet_utilization': fleet_util,
        'fuel_efficiency': fuel_efficiency,
        'fuel_cost': float(fuel_cost),
        'maint_cost': float(maint_cost),
        'other_cost': float(other_cost),
        'total_op_cost': total_op_cost,
        'vehicle_rois': vehicle_rois,
        'completed_trips': completed,
        'cancelled_trips': cancelled,
        'total_trips': completed + cancelled,
    }
    return render(request, 'reports/analytics.html', context)


@login_required
def export_csv(request, model_name):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{model_name}.csv"'
    writer = csv.writer(response)

    if model_name == 'vehicles':
        writer.writerow(['Registration', 'Name', 'Model', 'Type', 'Max Load (kg)', 'Odometer (km)',
                         'Acquisition Cost', 'Status', 'Region'])
        for v in Vehicle.objects.all():
            writer.writerow([v.registration_number, v.name, v.model, v.vehicle_type,
                            v.max_load_capacity, v.odometer, v.acquisition_cost, v.status, v.region])

    elif model_name == 'drivers':
        writer.writerow(['Name', 'License Number', 'License Category', 'License Expiry',
                         'Contact', 'Safety Score', 'Status'])
        for d in Driver.objects.all():
            writer.writerow([d.name, d.license_number, d.license_category,
                            d.license_expiry_date, d.contact_number, d.safety_score, d.status])

    elif model_name == 'trips':
        writer.writerow(['ID', 'Vehicle', 'Driver', 'Source', 'Destination', 'Cargo (kg)',
                         'Distance (km)', 'Status', 'Created'])
        for t in Trip.objects.select_related('vehicle', 'driver').all():
            writer.writerow([t.id, t.vehicle.registration_number, t.driver.name,
                            t.source, t.destination, t.cargo_weight, t.planned_distance,
                            t.status, t.created_at])

    elif model_name == 'fuel':
        writer.writerow(['Vehicle', 'Trip', 'Liters', 'Cost', 'Date'])
        for f in FuelLog.objects.select_related('vehicle').all():
            writer.writerow([f.vehicle.registration_number, f.trip_id, f.liters, f.cost, f.date])

    return response


@login_required
def export_pdf(request):
    if not HAS_XHTML2PDF:
        return HttpResponse('PDF export requires xhtml2pdf. Install with: pip install xhtml2pdf', status=501)

    vehicles = Vehicle.objects.all()
    completed_trips = Trip.objects.filter(status=Trip.Status.COMPLETED).count()
    total_op_cost = float(FuelLog.objects.aggregate(Sum('cost'))['cost__sum'] or 0) \
                  + float(MaintenanceRecord.objects.aggregate(Sum('cost'))['cost__sum'] or 0)

    html = get_template('reports/pdf_report.html').render({
        'vehicles': vehicles,
        'completed_trips': completed_trips,
        'total_op_cost': round(total_op_cost, 2),
        'generated_at': __import__('datetime').datetime.now(),
    })
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="transitops_report.pdf"'
    pisa.CreatePDF(io.BytesIO(html.encode('UTF-8')), dest=response)
    return response
