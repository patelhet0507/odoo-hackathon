import os
import django
from datetime import date, timedelta
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'transitops.settings')
django.setup()

from django.contrib.auth import get_user_model
from fleet.models import Vehicle, Driver, Trip, MaintenanceRecord, FuelLog, Expense
from django.utils import timezone

User = get_user_model()

VEHICLES = [
    {'reg': 'NY-849-TX', 'name': 'Volvo FH16', 'model': 'FH16 Heavy Duty', 'type': Vehicle.Type.TRUCK, 'cap': 24000, 'odo': 125000, 'cost': 150000, 'status': Vehicle.Status.ON_TRIP, 'region': 'Northeast'},
    {'reg': 'TX-221-OP', 'name': 'Freightliner M2', 'model': 'M2 Delivery Box Truck', 'type': Vehicle.Type.TRUCK, 'cap': 12000, 'odo': 85000, 'cost': 95000, 'status': Vehicle.Status.IN_SHOP, 'region': 'South'},
    {'reg': 'CA-909-LP', 'name': 'Mercedes Sprinter', 'model': 'Sprinter 3500', 'type': Vehicle.Type.VAN, 'cap': 3500, 'odo': 45000, 'cost': 60000, 'status': Vehicle.Status.AVAILABLE, 'region': 'West'},
    {'reg': 'IL-445-ZK', 'name': 'Peterbilt 579', 'model': '579 Long Haul', 'type': Vehicle.Type.TRUCK, 'cap': 36000, 'odo': 210000, 'cost': 180000, 'status': Vehicle.Status.ON_TRIP, 'region': 'Midwest'},
    {'reg': 'FL-771-MN', 'name': 'Kenworth T680', 'model': 'T680 Next Gen', 'type': Vehicle.Type.TRUCK, 'cap': 32000, 'odo': 67000, 'cost': 165000, 'status': Vehicle.Status.AVAILABLE, 'region': 'Southeast'},
    {'reg': 'WA-332-RS', 'name': 'Ford Transit 350', 'model': 'Transit Cargo Van', 'type': Vehicle.Type.VAN, 'cap': 3800, 'odo': 31000, 'cost': 48000, 'status': Vehicle.Status.ON_TRIP, 'region': 'West'},
    {'reg': 'OH-118-JK', 'name': 'International LT625', 'model': 'LT625 Sleeper', 'type': Vehicle.Type.TRUCK, 'cap': 28000, 'odo': 158000, 'cost': 140000, 'status': Vehicle.Status.IN_SHOP, 'region': 'Midwest'},
    {'reg': 'AZ-564-BV', 'name': 'RAM ProMaster 2500', 'model': 'ProMaster Cargo', 'type': Vehicle.Type.VAN, 'cap': 4200, 'odo': 22000, 'cost': 42000, 'status': Vehicle.Status.AVAILABLE, 'region': 'West'},
    {'reg': 'GA-892-WX', 'name': 'Mack Anthem', 'model': 'Anthem 70" Sleeper', 'type': Vehicle.Type.TRUCK, 'cap': 34000, 'odo': 93000, 'cost': 172000, 'status': Vehicle.Status.ON_TRIP, 'region': 'Southeast'},
    {'reg': 'CO-223-NP', 'name': 'Isuzu NPR HD', 'model': 'NPR HD Box Truck', 'type': Vehicle.Type.TRUCK, 'cap': 10000, 'odo': 51000, 'cost': 72000, 'status': Vehicle.Status.AVAILABLE, 'region': 'West'},
]

DRIVERS = [
    {'name': 'Marcus Johnson', 'license': 'TRP-9021', 'cat': Driver.LicenseCategory.E, 'exp': 365, 'contact': '+1-555-0192', 'score': 94, 'status': Driver.Status.ON_TRIP},
    {'name': 'Sarah Jenkins', 'license': 'TRP-9044', 'cat': Driver.LicenseCategory.E, 'exp': 500, 'contact': '+1-555-0143', 'score': 81, 'status': Driver.Status.ON_TRIP},
    {'name': 'Alex Ramirez', 'license': 'TRP-9088', 'cat': Driver.LicenseCategory.B, 'exp': -10, 'contact': '+1-555-0111', 'score': 88, 'status': Driver.Status.AVAILABLE},
    {'name': 'Emily Chen', 'license': 'TRP-9123', 'cat': Driver.LicenseCategory.C, 'exp': 180, 'contact': '+1-555-0176', 'score': 92, 'status': Driver.Status.AVAILABLE},
    {'name': 'James Wilson', 'license': 'TRP-9156', 'cat': Driver.LicenseCategory.E, 'exp': 730, 'contact': '+1-555-0134', 'score': 76, 'status': Driver.Status.ON_TRIP},
    {'name': 'Priya Sharma', 'license': 'TRP-9189', 'cat': Driver.LicenseCategory.D, 'exp': 90, 'contact': '+1-555-0188', 'score': 95, 'status': Driver.Status.AVAILABLE},
    {'name': 'Carlos Mendez', 'license': 'TRP-9221', 'cat': Driver.LicenseCategory.E, 'exp': 400, 'contact': '+1-555-0165', 'score': 85, 'status': Driver.Status.ON_TRIP},
]

TRIPS = [
    {'vehicle_idx': 0, 'driver_idx': 0, 'source': 'Chicago, IL', 'dest': 'Dallas, TX', 'cargo': 18000, 'dist': 1550, 'status': Trip.Status.DISPATCHED, 'hours_ago': 6},
    {'vehicle_idx': 3, 'driver_idx': 1, 'source': 'New York, NY', 'dest': 'Chicago, IL', 'cargo': 30000, 'dist': 1300, 'status': Trip.Status.DISPATCHED, 'hours_ago': 4},
    {'vehicle_idx': 2, 'driver_idx': 2, 'source': 'Los Angeles, CA', 'dest': 'San Francisco, CA', 'cargo': 2000, 'dist': 610, 'status': Trip.Status.COMPLETED, 'hours_ago': -72, 'actual_dist': 615, 'fuel': 75},
    {'vehicle_idx': 5, 'driver_idx': 3, 'source': 'Seattle, WA', 'dest': 'Portland, OR', 'cargo': 1800, 'dist': 280, 'status': Trip.Status.DISPATCHED, 'hours_ago': 2},
    {'vehicle_idx': 8, 'driver_idx': 6, 'source': 'Atlanta, GA', 'dest': 'Miami, FL', 'cargo': 22000, 'dist': 1080, 'status': Trip.Status.DISPATCHED, 'hours_ago': 8},
    {'vehicle_idx': 4, 'driver_idx': 4, 'source': 'Detroit, MI', 'dest': 'Boston, MA', 'cargo': 15000, 'dist': 950, 'status': Trip.Status.COMPLETED, 'hours_ago': -120, 'actual_dist': 965, 'fuel': 110},
    {'vehicle_idx': 1, 'driver_idx': 5, 'source': 'Houston, TX', 'dest': 'Phoenix, AZ', 'cargo': 8000, 'dist': 1400, 'status': Trip.Status.CANCELLED, 'hours_ago': -48},
]

MAINTENANCE = [
    {'vehicle_idx': 0, 'desc': 'Routine engine diagnostics and brake system calibration. Changed oil filters.', 'type': 'Routine Service', 'sched': -45, 'comp': -45, 'cost': 450, 'status': MaintenanceRecord.Status.CLOSED, 'notes': 'All diagnostics passed. Brake pads at 85%.'},
    {'vehicle_idx': 1, 'desc': 'Scheduled gearbox service and transmission oil replacement. Diagnostics flagging error 58.', 'type': 'Repair', 'sched': 0, 'cost': 1200, 'status': MaintenanceRecord.Status.OPEN, 'notes': 'Vehicle in shop. Parts ordered.'},
    {'vehicle_idx': 2, 'desc': 'Tire rotation and minor cosmetic scratch repair.', 'type': 'Maintenance', 'sched': -13, 'comp': -13, 'cost': 200, 'status': MaintenanceRecord.Status.CLOSED, 'notes': 'Completed successfully.'},
    {'vehicle_idx': 4, 'desc': 'Annual inspection and emission test.', 'type': 'Routine Service', 'sched': -60, 'comp': -60, 'cost': 350, 'status': MaintenanceRecord.Status.CLOSED, 'notes': 'Passed all checks.'},
    {'vehicle_idx': 6, 'desc': 'Transmission overhaul - synchronizer rings worn.', 'type': 'Repair', 'sched': -5, 'cost': 3400, 'status': MaintenanceRecord.Status.OPEN, 'notes': 'Awaiting parts delivery.'},
    {'vehicle_idx': 3, 'desc': 'Oil change and filter replacement.', 'type': 'Maintenance', 'sched': -20, 'comp': -20, 'cost': 180, 'status': MaintenanceRecord.Status.CLOSED, 'notes': 'Routine maintenance completed.'},
    {'vehicle_idx': 8, 'desc': 'AC compressor replacement and refrigerant recharge.', 'type': 'Repair', 'sched': -3, 'comp': -1, 'cost': 890, 'status': MaintenanceRecord.Status.CLOSED, 'notes': 'AC functioning normally.'},
    {'vehicle_idx': 0, 'desc': 'Tire replacement - all 6 drive tires.', 'type': 'Maintenance', 'sched': -90, 'comp': -90, 'cost': 2400, 'status': MaintenanceRecord.Status.CLOSED, 'notes': 'New Michelin X Line installed.'},
    {'vehicle_idx': 7, 'desc': 'Pre-delivery inspection and software update.', 'type': 'Routine Service', 'sched': -10, 'comp': -10, 'cost': 150, 'status': MaintenanceRecord.Status.CLOSED, 'notes': 'All systems updated.'},
    {'vehicle_idx': 9, 'desc': 'Brake pad replacement - front and rear.', 'type': 'Maintenance', 'sched': -30, 'comp': -30, 'cost': 520, 'status': MaintenanceRecord.Status.CLOSED, 'notes': 'Ceramic pads installed.'},
]

FUEL_LOGS = [
    {'vehicle_idx': 0, 'trip_idx': 0, 'liters': 350, 'cost': 525, 'days_ago': 1},
    {'vehicle_idx': 2, 'trip_idx': 2, 'liters': 75, 'cost': 112.50, 'days_ago': 3},
    {'vehicle_idx': 5, 'trip_idx': 3, 'liters': 40, 'cost': 60, 'days_ago': 1},
    {'vehicle_idx': 8, 'trip_idx': 4, 'liters': 260, 'cost': 390, 'days_ago': 2},
    {'vehicle_idx': 4, 'trip_idx': 5, 'liters': 200, 'cost': 300, 'days_ago': 10},
    {'vehicle_idx': 0, 'trip_idx': 0, 'liters': 180, 'cost': 270, 'days_ago': 0},
]

EXPENSES = [
    {'vehicle_idx': 0, 'trip_idx': 0, 'type': Expense.Type.TOLL, 'amount': 45, 'desc': 'I-90 Expressway Tolls', 'days_ago': 0},
    {'vehicle_idx': 0, 'trip_idx': 0, 'type': Expense.Type.FUEL, 'amount': 525, 'desc': 'Refueling in St. Louis', 'days_ago': 1},
    {'vehicle_idx': 5, 'trip_idx': 3, 'type': Expense.Type.FUEL, 'amount': 60, 'desc': 'Fuel stop Tacoma, WA', 'days_ago': 1},
    {'vehicle_idx': 8, 'trip_idx': 4, 'type': Expense.Type.TOLL, 'amount': 32, 'desc': 'Florida Turnpike tolls', 'days_ago': 2},
    {'vehicle_idx': 4, 'trip_idx': 5, 'type': Expense.Type.FUEL, 'amount': 300, 'desc': 'Refueling in Toledo, OH', 'days_ago': 10},
    {'vehicle_idx': 8, 'trip_idx': 4, 'type': Expense.Type.FUEL, 'amount': 390, 'desc': 'Fuel stop in Savannah, GA', 'days_ago': 2},
    {'vehicle_idx': 3, 'trip_idx': 1, 'type': Expense.Type.TOLL, 'amount': 28, 'desc': 'Ohio Turnpike tolls', 'days_ago': 1},
    {'vehicle_idx': 0, 'trip_idx': 0, 'type': Expense.Type.OTHER, 'amount': 15, 'desc': 'Parking fee Chicago depot', 'days_ago': 0},
]

def seed_data():
    now = timezone.now()

    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser(username='admin', email='admin@transitops.com', password='admin123', first_name='Admin', last_name='User', role=User.Role.FLEET_MANAGER, phone='')
        print('Created admin user (admin / admin123)')
    else:
        print('Admin user already exists, skipping')

    existing_vehicles = {v.registration_number: v for v in Vehicle.objects.all()}
    vehicles = []
    for vd in VEHICLES:
        if vd['reg'] in existing_vehicles:
            vehicles.append(existing_vehicles[vd['reg']])
            continue
        v = Vehicle.objects.create(registration_number=vd['reg'], name=vd['name'], model=vd['model'], vehicle_type=vd['type'], max_load_capacity=vd['cap'], odometer=vd['odo'], acquisition_cost=vd['cost'], status=vd['status'], region=vd['region'])
        vehicles.append(v)
        print(f'  Created vehicle {vd["reg"]} ({vd["name"]})')

    existing_drivers = {d.license_number: d for d in Driver.objects.all()}
    drivers = []
    for dd in DRIVERS:
        if dd['license'] in existing_drivers:
            drivers.append(existing_drivers[dd['license']])
            continue
        d = Driver.objects.create(name=dd['name'], license_number=dd['license'], license_category=dd['cat'], license_expiry_date=date.today() + timedelta(days=dd['exp']), contact_number=dd['contact'], safety_score=dd['score'], status=dd['status'])
        drivers.append(d)
        print(f'  Created driver {dd["name"]} ({dd["license"]})')

    existing_trips = list(Trip.objects.all())
    trip_offset = len(existing_trips)
    trips = list(existing_trips)
    for i, td in enumerate(TRIPS):
        if i < trip_offset:
            continue
        vehicle = vehicles[td['vehicle_idx']]
        driver = drivers[td['driver_idx']]
        dispatched = now - timedelta(hours=td['hours_ago'])
        kwargs = dict(vehicle=vehicle, driver=driver, source=td['source'], destination=td['dest'], cargo_weight=td['cargo'], planned_distance=td['dist'], status=td['status'], dispatched_at=dispatched)
        if td['status'] == Trip.Status.COMPLETED:
            kwargs['actual_distance'] = td.get('actual_dist', td['dist'])
            kwargs['completed_at'] = dispatched + timedelta(hours=td['dist'] / 45)
            kwargs['fuel_consumed'] = td.get('fuel', 0)
        elif td['status'] == Trip.Status.CANCELLED:
            kwargs['completed_at'] = dispatched + timedelta(hours=2)
        t = Trip.objects.create(**kwargs)
        trips.append(t)
        print(f'  Created trip {td["source"]} -> {td["dest"]} ({td["status"]})')

    existing_maintenance = list(MaintenanceRecord.objects.all())
    maint_offset = len(existing_maintenance)
    for i, md in enumerate(MAINTENANCE):
        if i < maint_offset:
            continue
        vehicle = vehicles[md['vehicle_idx']]
        sched = date.today() + timedelta(days=md['sched'])
        kwargs = dict(vehicle=vehicle, description=md['desc'], maintenance_type=md['type'], scheduled_date=sched, cost=md['cost'], status=md['status'], notes=md.get('notes', ''))
        if md['status'] == MaintenanceRecord.Status.CLOSED and 'comp' in md:
            kwargs['completed_date'] = date.today() + timedelta(days=md['comp'])
        MaintenanceRecord.objects.create(**kwargs)
        print(f'  Created maintenance: {md["desc"][:50]}...')

    existing_fuel = list(FuelLog.objects.all())
    fuel_offset = len(existing_fuel)
    for i, fd in enumerate(FUEL_LOGS):
        if i < fuel_offset:
            continue
        FuelLog.objects.create(vehicle=vehicles[fd['vehicle_idx']], trip=trips[fd['trip_idx']], liters=fd['liters'], cost=fd['cost'], date=date.today() - timedelta(days=fd['days_ago']))
        print(f'  Created fuel log entry')

    existing_expenses = list(Expense.objects.all())
    exp_offset = len(existing_expenses)
    for i, ed in enumerate(EXPENSES):
        if i < exp_offset:
            continue
        Expense.objects.create(vehicle=vehicles[ed['vehicle_idx']], trip=trips[ed['trip_idx']], expense_type=ed['type'], amount=ed['amount'], description=ed['desc'], date=date.today() - timedelta(days=ed['days_ago']))
        print(f'  Created expense: {ed["desc"][:50]}...')

    counts = dict(vehicles=Vehicle.objects.count(), drivers=Driver.objects.count(), trips=Trip.objects.count(), maintenance=MaintenanceRecord.objects.count(), fuel_logs=FuelLog.objects.count(), expenses=Expense.objects.count())
    print(f'\nDone. {counts}')

if __name__ == '__main__':
    seed_data()
