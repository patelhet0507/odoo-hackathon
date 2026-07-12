from .models import User


def role_permissions(request):
    if not request.user.is_authenticated:
        return {
            'is_fleet_manager': False,
            'is_driver': False,
            'is_safety_officer': False,
            'is_financial_analyst': False,
            'can_manage_vehicles': False,
            'can_manage_drivers': False,
            'can_manage_trips': False,
            'can_manage_maintenance': False,
            'can_manage_fuel': False,
            'can_manage_expenses': False,
            'can_view_reports': False,
            'can_view_financials': False,
            'can_create_edit_delete': False,
            'is_read_only': False,
        }

    role = request.user.role
    is_fleet_manager = role == User.Role.FLEET_MANAGER
    is_driver_role = role == User.Role.DRIVER
    is_safety_officer = role == User.Role.SAFETY_OFFICER
    is_financial_analyst = role == User.Role.FINANCIAL_ANALYST

    return {
        'is_fleet_manager': is_fleet_manager,
        'is_driver': is_driver_role,
        'is_safety_officer': is_safety_officer,
        'is_financial_analyst': is_financial_analyst,
        'can_manage_vehicles': is_fleet_manager or is_safety_officer or is_financial_analyst,
        'can_manage_drivers': is_fleet_manager or is_safety_officer,
        'can_manage_trips': is_fleet_manager or is_driver_role,
        'can_manage_maintenance': is_fleet_manager or is_safety_officer,
        'can_manage_fuel': is_fleet_manager or is_financial_analyst,
        'can_manage_expenses': is_fleet_manager or is_financial_analyst,
        'can_view_reports': is_fleet_manager or is_financial_analyst or is_safety_officer,
        'can_view_financials': is_fleet_manager or is_financial_analyst,
        'can_create_edit_delete': is_fleet_manager,
        'is_read_only': not is_fleet_manager,
    }
