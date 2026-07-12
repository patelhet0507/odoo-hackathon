from django import forms
from django.utils import timezone
from .models import Vehicle, Driver, Trip, MaintenanceRecord, FuelLog, Expense


class VehicleForm(forms.ModelForm):
    class Meta:
        model = Vehicle
        fields = '__all__'
        widgets = {
            'registration_number': forms.TextInput(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'model': forms.TextInput(attrs={'class': 'form-control'}),
            'vehicle_type': forms.Select(attrs={'class': 'form-select'}),
            'max_load_capacity': forms.NumberInput(attrs={'class': 'form-control'}),
            'odometer': forms.NumberInput(attrs={'class': 'form-control'}),
            'acquisition_cost': forms.NumberInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'region': forms.TextInput(attrs={'class': 'form-control'}),
        }


class DriverForm(forms.ModelForm):
    class Meta:
        model = Driver
        fields = '__all__'
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'license_number': forms.TextInput(attrs={'class': 'form-control'}),
            'license_category': forms.Select(attrs={'class': 'form-select'}),
            'license_expiry_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'contact_number': forms.TextInput(attrs={'class': 'form-control'}),
            'safety_score': forms.NumberInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }


class TripForm(forms.ModelForm):
    class Meta:
        model = Trip
        fields = ['vehicle', 'driver', 'source', 'destination', 'cargo_weight', 'planned_distance']
        widgets = {
            'vehicle': forms.Select(attrs={'class': 'form-select'}),
            'driver': forms.Select(attrs={'class': 'form-select'}),
            'source': forms.TextInput(attrs={'class': 'form-control'}),
            'destination': forms.TextInput(attrs={'class': 'form-control'}),
            'cargo_weight': forms.NumberInput(attrs={'class': 'form-control'}),
            'planned_distance': forms.NumberInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['vehicle'].queryset = Vehicle.objects.filter(status=Vehicle.Status.AVAILABLE)
        self.fields['driver'].queryset = Driver.objects.filter(
            status=Driver.Status.AVAILABLE,
            license_expiry_date__gt=timezone.now().date(),
        )

    def clean_cargo_weight(self):
        weight = self.cleaned_data['cargo_weight']
        vehicle = self.cleaned_data.get('vehicle')
        if vehicle and weight > vehicle.max_load_capacity:
            raise forms.ValidationError(
                f"Cargo weight ({weight} kg) exceeds vehicle max load ({vehicle.max_load_capacity} kg)."
            )
        return weight


class TripCompleteForm(forms.ModelForm):
    class Meta:
        model = Trip
        fields = ['end_odometer', 'fuel_consumed', 'actual_distance']
        widgets = {
            'end_odometer': forms.NumberInput(attrs={'class': 'form-control'}),
            'fuel_consumed': forms.NumberInput(attrs={'class': 'form-control'}),
            'actual_distance': forms.NumberInput(attrs={'class': 'form-control'}),
        }


class MaintenanceForm(forms.ModelForm):
    class Meta:
        model = MaintenanceRecord
        fields = ['vehicle', 'description', 'maintenance_type', 'scheduled_date', 'cost', 'notes']
        widgets = {
            'vehicle': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'maintenance_type': forms.TextInput(attrs={'class': 'form-control'}),
            'scheduled_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'cost': forms.NumberInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['vehicle'].queryset = Vehicle.objects.exclude(status=Vehicle.Status.RETIRED)


class FuelLogForm(forms.ModelForm):
    class Meta:
        model = FuelLog
        fields = ['vehicle', 'trip', 'liters', 'cost', 'date']
        widgets = {
            'vehicle': forms.Select(attrs={'class': 'form-select'}),
            'trip': forms.Select(attrs={'class': 'form-select'}),
            'liters': forms.NumberInput(attrs={'class': 'form-control'}),
            'cost': forms.NumberInput(attrs={'class': 'form-control'}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }


class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ['vehicle', 'trip', 'expense_type', 'amount', 'description', 'date']
        widgets = {
            'vehicle': forms.Select(attrs={'class': 'form-select'}),
            'trip': forms.Select(attrs={'class': 'form-select'}),
            'expense_type': forms.Select(attrs={'class': 'form-select'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }
