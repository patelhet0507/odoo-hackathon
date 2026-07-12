from datetime import date, timedelta
from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.conf import settings
from fleet.models import Driver


class Command(BaseCommand):
    help = 'Check driver license expiry and send reminders'

    def handle(self, *args, **options):
        soon = date.today() + timedelta(days=30)
        expiring = Driver.objects.filter(license_expiry_date__lte=soon, license_expiry_date__gte=date.today())
        expired = Driver.objects.filter(license_expiry_date__lt=date.today())

        for d in expiring:
            send_mail(
                subject=f'License Expiring Soon - {d.name}',
                message=f'Driver {d.name} (License: {d.license_number}) expires on {d.license_expiry_date}.',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[settings.DEFAULT_FROM_EMAIL],
                fail_silently=True,
            )
            self.stdout.write(f'Reminder sent for {d.name} (expires {d.license_expiry_date})')

        for d in expired:
            send_mail(
                subject=f'License EXPIRED - {d.name}',
                message=f'Driver {d.name} license {d.license_number} expired on {d.license_expiry_date}. Suspend immediately.',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[settings.DEFAULT_FROM_EMAIL],
                fail_silently=True,
            )
            self.stdout.write(f'Alert sent for {d.name} (expired {d.license_expiry_date})')

        self.stdout.write(f'Checked {expiring.count()} expiring, {expired.count()} expired.')
