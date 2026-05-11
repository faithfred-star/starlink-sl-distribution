import os
from django.core.wsgi import get_wsgi_application

# Make sure this says 'core.settings'
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

application = get_wsgi_application()