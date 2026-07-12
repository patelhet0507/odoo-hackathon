from django.urls import path
from . import views

app_name = 'fleet'

urlpatterns = [
    # Vehicles
    path('vehicles/', views.vehicle_list, name='vehicle_list'),
    path('vehicles/create/', views.vehicle_create, name='vehicle_create'),
    path('vehicles/<int:pk>/', views.vehicle_detail, name='vehicle_detail'),
    path('vehicles/<int:pk>/update/', views.vehicle_update, name='vehicle_update'),
    path('vehicles/<int:pk>/delete/', views.vehicle_delete, name='vehicle_delete'),
    path('vehicles/<int:pk>/upload-doc/', views.vehicle_upload_doc, name='vehicle_upload_doc'),
    path('vehicles/<int:pk>/delete-doc/<int:doc_id>/', views.vehicle_delete_doc, name='vehicle_delete_doc'),

    # Drivers
    path('drivers/', views.driver_list, name='driver_list'),
    path('drivers/create/', views.driver_create, name='driver_create'),
    path('drivers/<int:pk>/', views.driver_detail, name='driver_detail'),
    path('drivers/<int:pk>/update/', views.driver_update, name='driver_update'),
    path('drivers/<int:pk>/delete/', views.driver_delete, name='driver_delete'),

    # Trips
    path('trips/', views.trip_list, name='trip_list'),
    path('trips/create/', views.trip_create, name='trip_create'),
    path('trips/<int:pk>/', views.trip_detail, name='trip_detail'),
    path('trips/<int:pk>/dispatch/', views.trip_dispatch, name='trip_dispatch'),
    path('trips/<int:pk>/complete/', views.trip_complete, name='trip_complete'),
    path('trips/<int:pk>/cancel/', views.trip_cancel, name='trip_cancel'),

    # Maintenance
    path('maintenance/', views.maintenance_list, name='maintenance_list'),
    path('maintenance/create/', views.maintenance_create, name='maintenance_create'),
    path('maintenance/<int:pk>/close/', views.maintenance_close, name='maintenance_close'),

    # Fuel
    path('fuel/', views.fuel_list, name='fuel_list'),
    path('fuel/create/', views.fuel_create, name='fuel_create'),

    # Expenses
    path('expenses/', views.expense_list, name='expense_list'),
    path('expenses/create/', views.expense_create, name='expense_create'),

    # Audit Logs
    path('audit-logs/', views.audit_log_list, name='audit_log_list'),

    # Notifications
    path('notifications/', views.notification_list, name='notification_list'),
    path('notifications/unread-count/', views.notification_unread_count, name='notification_unread_count'),
    path('notifications/<int:pk>/mark-read/', views.notification_mark_read, name='notification_mark_read'),
    path('notifications/mark-all-read/', views.notification_mark_all_read, name='notification_mark_all_read'),
    path('notifications/<int:pk>/delete/', views.notification_delete, name='notification_delete'),

    # Live Tracking
    path('live-tracking/', views.live_tracking, name='live_tracking'),
    path('live-tracking/locations.json', views.vehicle_locations_json, name='vehicle_locations_json'),
    path('live-tracking/route/<int:pk>.json', views.vehicle_route_json, name='vehicle_route_json'),
    path('live-tracking/simulate/', views.simulate_location, name='simulate_location'),

    # Trip Timeline
    path('trips/<int:pk>/timeline/', views.trip_timeline, name='trip_timeline'),
]


