from django.contrib.auth import get_user_model
User = get_user_model()
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    def handle(self, *args, **options):
        if not User.objects.filter(username='inspcta_erp_admin').exists():
            User.objects.create_superuser('inspcta_erp_admin', 'hm.sayem.14@gmail.com', 'adminpass23')
