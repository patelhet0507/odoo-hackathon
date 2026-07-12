from django.contrib import admin
from .models import Vehicle, Driver, Trip, MaintenanceRecord, FuelLog, Expense, VehicleDocument

admin.site.register(Vehicle)
admin.site.register(Driver)
admin.site.register(Trip)
admin.site.register(MaintenanceRecord)
admin.site.register(FuelLog)
admin.site.register(Expense)
admin.site.register(VehicleDocument)
