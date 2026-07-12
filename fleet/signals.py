from django.db.models.signals import pre_save, post_save, post_delete
from django.dispatch import receiver
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.contrib.auth.signals import user_logged_in, user_logged_out
from transitops.middleware import get_current_request
from .models import Trip, MaintenanceRecord, Vehicle, Driver, FuelLog, Expense, AuditLog, Notification

User = get_user_model()


def create_audit_log(user, action, module, obj, request=None, previous_value='', new_value=''):
    if not user or not user.is_authenticated:
        return
    req = request or get_current_request()
    AuditLog.objects.create(
        user=user,
        username=user.username,
        role=user.role,
        action=action,
        module=module,
        object_id=str(obj.pk) if obj else '',
        object_repr=str(obj)[:200] if obj else '',
        previous_value=str(previous_value)[:500] if previous_value else '',
        new_value=str(new_value)[:500] if new_value else '',
        ip_address=req.META.get('REMOTE_ADDR') if req and hasattr(req, 'META') else None,
        user_agent=req.META.get('HTTP_USER_AGENT', '')[:500] if req and hasattr(req, 'META') else '',
    )


def create_notification(users, title, message, ntype, link=''):
    if not isinstance(users, list):
        users = [users]
    for u in users:
        Notification.objects.create(
            user=u, title=title, message=message,
            notification_type=ntype, link=link,
        )


@receiver(pre_save, sender=Trip)
def handle_trip_status_change(sender, instance, **kwargs):
    if instance.pk:
        try:
            old = Trip.objects.get(pk=instance.pk)
        except Trip.DoesNotExist:
            return

        if old.status != instance.status:
            if instance.status == Trip.Status.DISPATCHED and old.status == Trip.Status.DRAFT:
                instance.dispatched_at = timezone.now()
                Vehicle.objects.filter(pk=instance.vehicle_id).update(status=Vehicle.Status.ON_TRIP)
                Driver.objects.filter(pk=instance.driver_id).update(status=Driver.Status.ON_TRIP)

            elif instance.status == Trip.Status.COMPLETED and old.status == Trip.Status.DISPATCHED:
                instance.completed_at = timezone.now()
                Vehicle.objects.filter(pk=instance.vehicle_id).update(
                    status=Vehicle.Status.AVAILABLE,
                    odometer=instance.end_odometer or 0
                )
                Driver.objects.filter(pk=instance.driver_id).update(status=Driver.Status.AVAILABLE)

            elif instance.status == Trip.Status.CANCELLED and old.status in (Trip.Status.DRAFT, Trip.Status.DISPATCHED):
                Vehicle.objects.filter(pk=instance.vehicle_id).update(status=Vehicle.Status.AVAILABLE)
                Driver.objects.filter(pk=instance.driver_id).update(status=Driver.Status.AVAILABLE)


@receiver(post_save, sender=MaintenanceRecord)
def handle_maintenance_status(sender, instance, created, **kwargs):
    if created and instance.status == MaintenanceRecord.Status.OPEN:
        Vehicle.objects.filter(pk=instance.vehicle_id).update(status=Vehicle.Status.IN_SHOP)


@receiver(pre_save, sender=MaintenanceRecord)
def handle_maintenance_close(sender, instance, **kwargs):
    if instance.pk:
        try:
            old = MaintenanceRecord.objects.get(pk=instance.pk)
        except MaintenanceRecord.DoesNotExist:
            return

        if old.status == MaintenanceRecord.Status.OPEN and instance.status == MaintenanceRecord.Status.CLOSED:
            vehicle = instance.vehicle
            if vehicle.status != Vehicle.Status.RETIRED:
                has_open = MaintenanceRecord.objects.filter(
                    vehicle=vehicle, status=MaintenanceRecord.Status.OPEN
                ).exclude(pk=instance.pk).exists()
                if not has_open:
                    Vehicle.objects.filter(pk=vehicle.pk).update(status=Vehicle.Status.AVAILABLE)
            instance.completed_date = timezone.now().date()


# ---- AUTO NOTIFICATIONS ----

@receiver(post_save, sender=Trip)
def trip_notification(sender, instance, created, **kwargs):
    if created:
        managers = User.objects.filter(role=User.Role.FLEET_MANAGER)
        create_notification(
            list(managers), f"Trip #{instance.id} Created",
            f"New trip from {instance.source} → {instance.destination}",
            Notification.Type.TRIP, f"/fleet/trips/{instance.id}/"
        )


@receiver(post_save, sender=FuelLog)
def fuel_notification(sender, instance, created, **kwargs):
    if created:
        managers = User.objects.filter(role__in=[User.Role.FLEET_MANAGER, User.Role.FINANCIAL_ANALYST])
        create_notification(
            list(managers), f"Fuel Log: {instance.vehicle.registration_number}",
            f"{instance.liters}L recorded at ₹{instance.cost} on {instance.date}",
            Notification.Type.FUEL, "/fleet/fuel/"
        )


@receiver(post_save, sender=Expense)
def expense_notification(sender, instance, created, **kwargs):
    if created:
        managers = User.objects.filter(role__in=[User.Role.FLEET_MANAGER, User.Role.FINANCIAL_ANALYST])
        create_notification(
            list(managers), f"Expense: {instance.get_expense_type_display()} on {instance.vehicle.registration_number}",
            f"₹{instance.amount} - {instance.description[:50]}",
            Notification.Type.EXPENSE, "/fleet/expenses/"
        )


@receiver(post_save, sender=Driver)
def driver_license_notification(sender, instance, **kwargs):
    from datetime import date, timedelta
    today = date.today()
    if instance.license_expiry_date and today <= instance.license_expiry_date <= today + timedelta(days=30):
        managers = User.objects.filter(role=User.Role.FLEET_MANAGER)
        create_notification(
            list(managers), f"License Expiring: {instance.name}",
            f"License {instance.license_number} expires on {instance.license_expiry_date}",
            Notification.Type.LICENSE, f"/fleet/drivers/{instance.pk}/"
        )


# ---- AUDIT LOGS ----

@receiver(post_save, sender=Trip)
def audit_trip(sender, instance, created, **kwargs):
    req = get_current_request()
    user = getattr(req, 'user', None) if req else None
    if created:
        create_audit_log(user, 'create', 'Trip', instance, req)
    else:
        create_audit_log(user, 'update', 'Trip', instance, req)


@receiver(post_save, sender=Vehicle)
def audit_vehicle(sender, instance, created, **kwargs):
    req = get_current_request()
    user = getattr(req, 'user', None) if req else None
    if created:
        create_audit_log(user, 'create', 'Vehicle', instance, req)
    else:
        create_audit_log(user, 'update', 'Vehicle', instance, req)


@receiver(post_save, sender=Driver)
def audit_driver(sender, instance, created, **kwargs):
    req = get_current_request()
    user = getattr(req, 'user', None) if req else None
    if created:
        create_audit_log(user, 'create', 'Driver', instance, req)
    else:
        create_audit_log(user, 'update', 'Driver', instance, req)


@receiver(post_save, sender=MaintenanceRecord)
def audit_maintenance(sender, instance, created, **kwargs):
    req = get_current_request()
    user = getattr(req, 'user', None) if req else None
    if created:
        create_audit_log(user, 'create', 'Maintenance', instance, req)
    else:
        create_audit_log(user, 'update', 'Maintenance', instance, req)


@receiver(post_save, sender=FuelLog)
def audit_fuel(sender, instance, created, **kwargs):
    req = get_current_request()
    user = getattr(req, 'user', None) if req else None
    if created:
        create_audit_log(user, 'create', 'FuelLog', instance, req)
    else:
        create_audit_log(user, 'update', 'FuelLog', instance, req)


@receiver(post_save, sender=Expense)
def audit_expense(sender, instance, created, **kwargs):
    req = get_current_request()
    user = getattr(req, 'user', None) if req else None
    if created:
        create_audit_log(user, 'create', 'Expense', instance, req)
    else:
        create_audit_log(user, 'update', 'Expense', instance, req)


@receiver(post_delete, sender=Trip)
def audit_trip_delete(sender, instance, **kwargs):
    create_audit_log(None, 'delete', 'Trip', instance)


@receiver(post_delete, sender=Vehicle)
def audit_vehicle_delete(sender, instance, **kwargs):
    create_audit_log(None, 'delete', 'Vehicle', instance)


@receiver(post_delete, sender=Driver)
def audit_driver_delete(sender, instance, **kwargs):
    create_audit_log(None, 'delete', 'Driver', instance)


# ---- LOGIN/LOGOUT AUDIT ----

@receiver(user_logged_in)
def audit_login(sender, request, user, **kwargs):
    AuditLog.objects.create(
        user=user, username=user.username, role=user.role,
        action='login', module='Auth',
        ip_address=request.META.get('REMOTE_ADDR'),
        user_agent=request.META.get('HTTP_USER_AGENT', '')[:500],
    )


@receiver(user_logged_out)
def audit_logout(sender, request, user, **kwargs):
    if user and user.is_authenticated:
        AuditLog.objects.create(
            user=user, username=user.username, role=user.role,
            action='logout', module='Auth',
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', '')[:500],
        )
