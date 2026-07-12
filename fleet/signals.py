from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.utils import timezone
from .models import Trip, MaintenanceRecord, Vehicle, Driver


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
