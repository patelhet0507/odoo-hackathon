import os
import django
from datetime import date, timedelta
from decimal import Decimal

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'transitops.settings')
django.setup()

from django.contrib.auth import get_user_model
from fleet.models import Vehicle, Driver, Trip, MaintenanceRecord, FuelLog, Expense

User = get_user_model()

def seed_data():
    print("Clearing old data...")
    Expense.objects.all().delete()
    FuelLog.objects.all().delete()
    MaintenanceRecord.objects.all().delete()
    Trip.objects.all().delete()
    Driver.objects.all().delete()
    Vehicle.objects.all().delete()
    User.objects.all().delete()

    print("Creating superuser...")
    admin_user = User.objects.create_superuser(
        username='admin',
        email='admin@transitops.com',
        password='admin123',
        first_name='Dhvani',
        last_name='Patel',
        role=User.Role.FLEET_MANAGER,
        phone=''
    )
    print("Superuser created: username: 'admin', password: 'admin123'")

    print("Creating vehicles...")
    v1 = Vehicle.objects.create(
        registration_number="NY-849-TX",
        name="Volvo FH16",
        model="FH16 Heavy Duty M2",
        vehicle_type=Vehicle.Type.TRUCK,
        max_load_capacity=24000.00,
        odometer=125000,
        acquisition_cost=150000.00,
        status=Vehicle.Status.ON_TRIP,
        region="Northeast"
    )

    v2 = Vehicle.objects.create(
        registration_number="TX-221-OP",
        name="Freightliner M2",
        model="M2 Delivery Box Truck",
        vehicle_type=Vehicle.Type.TRUCK,
        max_load_capacity=12000.00,
        odometer=85000,
        acquisition_cost=95000.00,
        status=Vehicle.Status.IN_SHOP,
        region="South"
    )

    v3 = Vehicle.objects.create(
        registration_number="CA-909-LP",
        name="Mercedes Sprinter",
        model="Sprinter Sprinter",
        vehicle_type=Vehicle.Type.VAN,
        max_load_capacity=3500.00,
        odometer=45000,
        acquisition_cost=60000.00,
        status=Vehicle.Status.AVAILABLE,  # Idle in mockup
        region="West"
    )

    v4 = Vehicle.objects.create(
        registration_number="IL-445-ZK",
        name="Peterbilt 579",
        model="579 Long Haul",
        vehicle_type=Vehicle.Type.TRUCK,
        max_load_capacity=36000.00,
        odometer=210000,
        acquisition_cost=180000.00,
        status=Vehicle.Status.ON_TRIP,
        region="Midwest"
    )

    print("Creating drivers...")
    d1 = Driver.objects.create(
        name="Marcus Johnson",
        license_number="TRP-9021",
        license_category=Driver.LicenseCategory.E,
        license_expiry_date=date.today() + timedelta(days=365),
        contact_number="+1-555-0192",
        safety_score=94,
        status=Driver.Status.ON_TRIP
    )

    d2 = Driver.objects.create(
        name="Sarah Jenkins",
        license_number="TRP-9044",
        license_category=Driver.LicenseCategory.E,
        license_expiry_date=date.today() + timedelta(days=500),
        contact_number="+1-555-0143",
        safety_score=81,
        status=Driver.Status.ON_TRIP
    )

    d3 = Driver.objects.create(
        name="Alex Ramirez",
        license_number="TRP-9088",
        license_category=Driver.LicenseCategory.B,
        license_expiry_date=date.today() - timedelta(days=10), # Expired license
        contact_number="+1-555-0111",
        safety_score=88,
        status=Driver.Status.AVAILABLE
    )

    print("Creating trips...")
    # Active Trip for Marcus
    t1 = Trip.objects.create(
        vehicle=v1,
        driver=d1,
        source="Chicago, IL",
        destination="Dallas, TX",
        cargo_weight=18000.00,
        planned_distance=1550.00,
        status=Trip.Status.DISPATCHED,
        dispatched_at=django.utils.timezone.now() - timedelta(hours=6),
        start_odometer=124000
    )

    # Active Trip for Sarah
    t2 = Trip.objects.create(
        vehicle=v4,
        driver=d2,
        source="New York, NY",
        destination="Chicago, IL",
        cargo_weight=30000.00,
        planned_distance=1300.00,
        status=Trip.Status.DISPATCHED,
        dispatched_at=django.utils.timezone.now() - timedelta(hours=4),
        start_odometer=209000
    )

    # Completed Trip
    t3 = Trip.objects.create(
        vehicle=v3,
        driver=d3,
        source="Los Angeles, CA",
        destination="San Francisco, CA",
        cargo_weight=2000.00,
        planned_distance=610.00,
        actual_distance=615.00,
        status=Trip.Status.COMPLETED,
        dispatched_at=django.utils.timezone.now() - timedelta(days=3),
        completed_at=django.utils.timezone.now() - timedelta(days=2, hours=16),
        start_odometer=44000,
        end_odometer=44615,
        fuel_consumed=75.00
    )

    print("Creating maintenance records...")
    # Closed maintenance for NY-849-TX
    MaintenanceRecord.objects.create(
        vehicle=v1,
        description="Routine engine diagnostics and brake systems calibration. Changed oil filters.",
        maintenance_type="Routine Service",
        scheduled_date=date.today() - timedelta(days=45),
        completed_date=date.today() - timedelta(days=45),
        cost=450.00,
        status=MaintenanceRecord.Status.CLOSED,
        notes="All diagnostics passed. Brake pads at 85%."
    )

    # Open maintenance for TX-221-OP
    MaintenanceRecord.objects.create(
        vehicle=v2,
        description="Scheduled gearbox service and transmission oil replacement. Diagnostics flagging error 58.",
        maintenance_type="Repair",
        scheduled_date=date.today(),
        cost=1200.00,
        status=MaintenanceRecord.Status.OPEN,
        notes="Vehicle in shop. Parts ordered."
    )

    # Idle vehicle CA-909-LP last maintenance
    MaintenanceRecord.objects.create(
        vehicle=v3,
        description="Tire rotation and minor cosmetic scratch repair.",
        maintenance_type="Maintenance",
        scheduled_date=date.today() - timedelta(days=13),
        completed_date=date.today() - timedelta(days=13),
        cost=200.00,
        status=MaintenanceRecord.Status.CLOSED,
        notes="Completed successfully."
    )

    print("Creating fuel logs...")
    FuelLog.objects.create(
        vehicle=v1,
        trip=t1,
        liters=350.00,
        cost=525.00,
        date=date.today() - timedelta(days=1)
    )
    FuelLog.objects.create(
        vehicle=v3,
        trip=t3,
        liters=75.00,
        cost=112.50,
        date=date.today() - timedelta(days=3)
    )

    print("Creating expenses...")
    Expense.objects.create(
        vehicle=v1,
        trip=t1,
        expense_type=Expense.Type.TOLL,
        amount=45.00,
        description="I-90 Expressway Tolls",
        date=date.today()
    )
    Expense.objects.create(
        vehicle=v1,
        trip=t1,
        expense_type=Expense.Type.FUEL,
        amount=525.00,
        description="Refueling in St. Louis",
        date=date.today() - timedelta(days=1)
    )

    print("Database seeding completed successfully!")

if __name__ == "__main__":
    seed_data()
