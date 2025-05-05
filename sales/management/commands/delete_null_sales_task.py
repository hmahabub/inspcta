from django.core.management.base import BaseCommand
from sales.models import Task

class Command(BaseCommand):
	help = 'Migrate operation expenditure data with duplicate phone number handling'

	def handle(self, *args, **options):
		# Delete records with empty description and amount = 0
		deleted_count, _ = Task.objects.filter(description="", cost=0).delete()
		self.stdout.write(self.style.SUCCESS(f"Deleted {deleted_count} records."))
