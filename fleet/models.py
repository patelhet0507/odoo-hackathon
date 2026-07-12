from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from django.conf import settings


class Vehicle(models.Model):
    class Status(models.TextChoices):
        AVAILABLE = 'Available', 'Available'
        ON_TRIP = 'On Trip', 'On Trip'
        IN_SHOP = 'In Shop', 'In Shop'
        RETIRED = 'Retired', 'Retired'

    class Type(models.TextChoices):
        TRUCK = 'Truck', 'Truck'
        VAN = 'Van', 'Van'
        CAR = 'Car', 'Car'
        BUS = 'Bus', 'Bus'

    registration_number = models.CharField(max_length=50, unique=True, db_index=True)
    name = models.CharField(max_length=100, db_index=True)
    model = models.CharField(max_length=100, blank=True, db_index=True)
    vehicle_type = models.CharField(max_length=20, choices=Type.choices, default=Type.VAN, db_index=True)
    max_load_capacity = models.DecimalField(max_digits=10, decimal_places=2, help_text='kg')
    odometer = models.IntegerField(default=0, help_text='km')
    acquisition_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.AVAILABLE, db_index=True)
    region = models.CharField(max_length=100, blank=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.registration_number} - {self.name} ({self.status})"

    @property
    def active_trip(self):
        return self.trips.filter(status='Dispatched').first()

    @property
    def active_driver(self):
        trip = self.active_trip
        return trip.driver if trip else None

    @property
    def last_maintenance_record(self):
        return self.maintenance_records.order_by('-completed_date', '-scheduled_date').first()

    @property
    def health_score(self):
        if self.status == self.Status.IN_SHOP:
            return 58
        elif self.status == self.Status.ON_TRIP:
            return 80 + (self.pk % 15)
        else:
            return 85 + (self.pk % 10)


class Driver(models.Model):
    class Status(models.TextChoices):
        AVAILABLE = 'Available', 'Available'
        ON_TRIP = 'On Trip', 'On Trip'
        OFF_DUTY = 'Off Duty', 'Off Duty'
        SUSPENDED = 'Suspended', 'Suspended'

    class LicenseCategory(models.TextChoices):
        A = 'A', 'A - Motorcycle'
        B = 'B', 'B - Light Vehicle'
        C = 'C', 'C - Medium Vehicle'
        D = 'D', 'D - Bus'
        E = 'E', 'E - Heavy Vehicle'

    name = models.CharField(max_length=100, db_index=True)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='driver_profile')
    license_number = models.CharField(max_length=50, unique=True, db_index=True)
    license_category = models.CharField(max_length=10, choices=LicenseCategory.choices, default=LicenseCategory.B)
    license_expiry_date = models.DateField()
    contact_number = models.CharField(max_length=20)
    safety_score = models.IntegerField(default=100, validators=[MinValueValidator(0), MaxValueValidator(100)])
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.AVAILABLE, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.license_number}) - {self.status}"

    @property
    def license_is_expired(self):
        return timezone.now().date() > self.license_expiry_date


class Trip(models.Model):
    class Status(models.TextChoices):
        DRAFT = 'Draft', 'Draft'
        DISPATCHED = 'Dispatched', 'Dispatched'
        COMPLETED = 'Completed', 'Completed'
        CANCELLED = 'Cancelled', 'Cancelled'

    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='trips')
    driver = models.ForeignKey(Driver, on_delete=models.CASCADE, related_name='trips')
    source = models.CharField(max_length=200)
    destination = models.CharField(max_length=200)
    cargo_weight = models.DecimalField(max_digits=10, decimal_places=2, help_text='kg')
    planned_distance = models.DecimalField(max_digits=10, decimal_places=2, help_text='km')
    actual_distance = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text='km')
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT, db_index=True)
    dispatched_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    start_odometer = models.IntegerField(null=True, blank=True)
    end_odometer = models.IntegerField(null=True, blank=True)
    fuel_consumed = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text='L')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Trips'

    def __str__(self):
        return f"Trip {self.id}: {self.source} → {self.destination} ({self.status})"


class MaintenanceRecord(models.Model):
    class Status(models.TextChoices):
        OPEN = 'Open', 'Open'
        CLOSED = 'Closed', 'Closed'

    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='maintenance_records')
    description = models.TextField()
    maintenance_type = models.CharField(max_length=100, blank=True)
    scheduled_date = models.DateField()
    completed_date = models.DateField(null=True, blank=True)
    cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.OPEN)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.vehicle.registration_number} - {self.description[:30]} ({self.status})"


class FuelLog(models.Model):
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='fuel_logs')
    trip = models.ForeignKey(Trip, on_delete=models.SET_NULL, null=True, blank=True, related_name='fuel_logs')
    liters = models.DecimalField(max_digits=10, decimal_places=2)
    cost = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"{self.vehicle.registration_number} - {self.liters}L on {self.date}"


class Expense(models.Model):
    class Type(models.TextChoices):
        TOLL = 'Toll', 'Toll'
        MAINTENANCE = 'Maintenance', 'Maintenance'
        PARKING = 'Parking', 'Parking'
        FUEL = 'Fuel', 'Fuel'
        OTHER = 'Other', 'Other'

    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='expenses')
    trip = models.ForeignKey(Trip, on_delete=models.SET_NULL, null=True, blank=True, related_name='expenses')
    expense_type = models.CharField(max_length=20, choices=Type.choices, default=Type.OTHER)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True)
    date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"{self.vehicle.registration_number} - {self.expense_type} - ₹{self.amount}"


class VehicleDocument(models.Model):
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='documents')
    document_type = models.CharField(max_length=100)
    file = models.FileField(upload_to='documents/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.vehicle.registration_number} - {self.document_type}"


class AuditLog(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    username = models.CharField(max_length=150)
    role = models.CharField(max_length=20, blank=True)
    action = models.CharField(max_length=20, db_index=True)
    module = models.CharField(max_length=50, db_index=True)
    object_id = models.CharField(max_length=50, blank=True)
    object_repr = models.CharField(max_length=200, blank=True)
    previous_value = models.TextField(blank=True)
    new_value = models.TextField(blank=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.CharField(max_length=500, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Audit logs'

    def __str__(self):
        return f"{self.username} {self.action} {self.module} at {self.created_at}"


class Notification(models.Model):
    class Type(models.TextChoices):
        TRIP = 'trip', 'Trip'
        MAINTENANCE = 'maintenance', 'Maintenance'
        FUEL = 'fuel', 'Fuel'
        EXPENSE = 'expense', 'Expense'
        DRIVER = 'driver', 'Driver'
        VEHICLE = 'vehicle', 'Vehicle'
        SYSTEM = 'system', 'System'
        LICENSE = 'license', 'License'

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=200)
    message = models.TextField()
    notification_type = models.CharField(max_length=20, choices=Type.choices, default=Type.SYSTEM, db_index=True)
    link = models.CharField(max_length=300, blank=True)
    is_read = models.BooleanField(default=False, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"[{self.get_notification_type_display()}] {self.title}"


class VehicleLocation(models.Model):
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='locations')
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    speed = models.DecimalField(max_digits=6, decimal_places=1, default=0, help_text='km/h')
    heading = models.IntegerField(default=0, help_text='degrees')
    is_active = models.BooleanField(default=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.vehicle.registration_number} @ ({self.latitude}, {self.longitude})"


class Checkpoint(models.Model):
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE, related_name='checkpoints')
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    is_current_location = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']
        verbose_name_plural = 'Checkpoints'

    def __str__(self):
        return f"{self.name} (Trip #{self.trip_id})"


