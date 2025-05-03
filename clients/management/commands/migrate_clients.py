import json
import os
import csv
from datetime import datetime
from django.core.management.base import BaseCommand
from clients.models import Client  # Replace with your actual model

class Command(BaseCommand):
    help = 'Migrate client data with duplicate phone number handling'

    def add_arguments(self, parser):
        parser.add_argument(
            '--skip-duplicates',
            action='store_true',
            help='Skip clients with duplicate phone numbers'
        )
        parser.add_argument(
            '--update-duplicates',
            action='store_true',
            help='Update existing clients when phone numbers conflict'
        )

    def handle(self, *args, **options):
        json_file_path = os.path.join(os.path.dirname(__file__), 'client.json')
        log_file_path = os.path.join(os.path.dirname(__file__), 'log_file.csv')
        # keep_pks = [1]
        # Client.objects.exclude(pk__in=keep_pks).delete()

        with open(log_file_path, 'w', newline='') as csvfile:
            fieldnames = [
                'timestamp', 
                'old_pk', 
                'new_pk', 
                'action',
                'name',
                'status', 
                'error'
            ]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            def log_action(old_pk, new_pk, action, name, status, error=''):
                writer.writerow({
                    'timestamp': datetime.now().isoformat(),
                    'old_pk': old_pk,
                    'new_pk': new_pk,
                    'action': action,
                    'name': name,
                    'status': status,
                    'error': error
                })
        
            try:
                with open(json_file_path, 'r', encoding='utf-8') as json_file:
                    raw_content = json_file.read()
                    unescaped_content = raw_content.encode('utf-8').decode('unicode_escape')
                    if unescaped_content.startswith('"') and unescaped_content.endswith('"'):
                        unescaped_content = unescaped_content[1:-1]
                    clients_data = json.loads(unescaped_content)
                    
                    if isinstance(clients_data, str):
                        clients_data = json.loads(clients_data)
                        
            except FileNotFoundError:
                self.stdout.write(self.style.ERROR('client_regular.json file not found'))
                return
            except json.JSONDecodeError as e:
                self.stdout.write(self.style.ERROR(f'Invalid JSON format: {str(e)}'))
                return

            # Field configuration
            DEFAULT_VALUES = {
                'contact_person': '',
                'types': 'INT',
                'tax_id': '',
                'website': '',
                'notes': '',
            }
            
            FIELD_MAPPING = {
                'name': 'client_name',
                'phone': 'client_contact',
                'email': 'client_email',
                'address': 'client_address'
            }

            # Track processed phone numbers
            processed_phones = set()
            duplicate_count = 0
            success_count = 0

            for emp_data in clients_data:
                try:
                    if isinstance(emp_data, str):
                        emp_data = json.loads(emp_data)
                    
                    fields = emp_data['fields']
                    phone = fields.get('mobile')
                    old_pk = emp_data['pk']
                    name = fields.get('client_name', '')
                    
                    # Skip if phone is empty
                    if not phone:
                        phone = '+9999999999'
                        self.stdout.write(self.style.WARNING(f'Adding dummy phone no. to client {fields.get("name")} - +9999999999'))
                    
                    # Handle duplicate phone numbers
                    if phone in processed_phones:
                        if options['skip_duplicates']:
                            self.stdout.write(self.style.WARNING(f'Skipping duplicate phone: {phone} for {fields.get("name")}'))
                            duplicate_count += 1
                            continue
                        elif options['update_duplicates']:
                            # Update existing record
                            try:
                                client = Client.objects.get(phone=phone)
                                for target_field, source_field in FIELD_MAPPING.items():
                                    if source_field in fields:
                                        value = fields[source_field]
                                        setattr(client, target_field, value)
                                client.save()
                                self.stdout.write(self.style.SUCCESS(f'Updated client: {client.name}'))
                                success_count += 1
                                continue
                            except Client.DoesNotExist:
                                pass  # Fall through to create new
                    
                    # Create new client
                    client = Client()
                    for target_field, source_field in FIELD_MAPPING.items():
                        if source_field in fields:
                            value = fields[source_field]
                            setattr(client, target_field, value)
                    
                    for field, value in DEFAULT_VALUES.items():
                        setattr(client, field, value)
                    
                    client.save()
                    log_action(old_pk, client.pk, 'CREATE', name, 'SUCCESS')
                    processed_phones.add(phone)

                    success_count += 1
                    self.stdout.write(self.style.SUCCESS(f'Successfully migrated client: {client.name}-{client.phone}-{client.email}'))
                
                except Exception as e:
                    log_action(old_pk, '', 'CREATE/UPDATE', name, 'FAILED', str(e))
                    self.stdout.write(self.style.ERROR(f'Failed to migrate client {fields.get("name", "Unknown")}: {str(e)}'))

            # Summary
            self.stdout.write(self.style.SUCCESS(f'\nMigration Summary:'))
            self.stdout.write(self.style.SUCCESS(f'Successfully processed: {success_count}'))
            self.stdout.write(self.style.WARNING(f'Skipped duplicates: {duplicate_count}'))
            self.stdout.write(self.style.SUCCESS('Migration completed'))