from django.http import HttpResponse
from django.core.management import call_command
from io import StringIO


def cron_check_licenses(request):
    token = request.GET.get('token', '')
    if token != 'transitops-cron-secret':
        return HttpResponse('Forbidden', status=403)
    out = StringIO()
    call_command('check_licenses', stdout=out)
    return HttpResponse(out.getvalue())


