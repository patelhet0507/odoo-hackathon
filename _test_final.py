import django, os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'transitops.settings')
django.setup()
from django.test import Client
from django.contrib.auth import get_user_model
User = get_user_model()
client = Client()

tests = [
    ('admin', 'admin'),
    ('safety', 'safety'),
    ('finance', 'finance'),
    ('driver1', 'driver1'),
]

for uname, pw in tests:
    user = User.objects.get(username=uname)
    client.force_login(user)
    resp = client.get('/dashboard/')
    content = resp.content.decode()
    print(f'--- {uname} ({user.role}) ---')
    print(f'  Length: {len(resp.content)} bytes')
    print(f'  Has MyDashboard: {"My Dashboard" in content}')
    print(f'  Has FleetUtil: {"Fleet Utilization" in content}')
    print(f'  Has error page: {"Internal Server Error" in content}')
    if 'traceback' in content.lower():
        print('  !! TRACEBACK FOUND !!')
    client.logout()

# Check vehicle list for safety
client.force_login(User.objects.get(username='safety'))
resp = client.get('/fleet/vehicles/')
content = resp.content.decode()
print(f'\n--- safety/vehicles ---')
print(f'  Length: {len(resp.content)} bytes')
print(f'  Has Fleet Overview: {"Fleet Overview" in content}')
print(f'  Has Add button: {"Add Vehicle" in content}')
# Check that vehicle rows exist
import re
print(f'  Table rows: {len(re.findall(r"<tr", content))}')
client.logout()
