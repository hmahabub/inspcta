import json
import os
import csv
from datetime import datetime
from django.core.management.base import BaseCommand
from employees.models import Employee  # Replace with your actual model

class Command(BaseCommand):
    help = 'Migrate employee data with duplicate phone number handling'

    def generate_dummy_phone(self):
        """Generate a random dummy phone number with the given prefix"""
        return f"{random.randint(100000, 999999)}"

    def handle(self, *args, **options):
        json_file_path = os.path.join(os.path.dirname(__file__), 'employee_casual.json')
        log_file_path = os.path.join(os.path.dirname(__file__), 'employee_log_file_casual.csv')

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
                    employees_data = json.loads(unescaped_content)
                    
                    if isinstance(employees_data, str):
                        employees_data = json.loads(employees_data)
                        
            except FileNotFoundError:
                self.stdout.write(self.style.ERROR('employee_casual.json file not found'))
                return
            except json.JSONDecodeError as e:
                self.stdout.write(self.style.ERROR(f'Invalid JSON format: {str(e)}'))
                return

            # Field configuration
            DEFAULT_VALUES = {
                'marital_status': '',
                'is_regular': False,
                'department': 'Ops',
                'designation': 'Employee',
                'bank_name': '',
                'account_number': '',
                'emergency_contact_person': 'Placeholder',
                'relation_with_the_person': 'Other',
                'emergency_contact_1': '+999999999'
            }
            
            FIELD_MAPPING = {
                'name': 'name',
                'nid': 'nid',
                'phone': 'mobile',
                'bkash': 'bkash',
                'email': 'Email',
                'address': 'address'
            }


            # Track processed phone numbers
            processed_phones = set()
            duplicate_count = 0
            success_count = 0

            for emp_data in employees_data:
                try:
                    if isinstance(emp_data, str):
                        emp_data = json.loads(emp_data)
                    
                    fields = emp_data['fields']
                    phone = fields.get('mobile')
                    old_pk = emp_data['pk']
                    name = fields.get('name', '')

                    if not phone:
                        phone = '+9999999999'
                        self.stdout.write(self.style.WARNING(f'Adding dummy phone no. to employee {fields.get("name")} - +9999999999'))
                    
                    # Create new employee
                    employee = Employee()
                    for target_field, source_field in FIELD_MAPPING.items():
                        if source_field in fields:
                            value = fields[source_field]
                            setattr(employee, target_field, value)
                    
                    for field, value in DEFAULT_VALUES.items():
                        setattr(employee, field, value)
                    
                    employee.save()
                    log_action(old_pk, employee.pk, 'CREATE', name, 'SUCCESS')
                    processed_phones.add(phone)
                    success_count += 1
                    self.stdout.write(self.style.SUCCESS(f'Successfully migrated employee: {employee.name}'))
                
                except Exception as e:
                    log_action(old_pk, '', 'CREATE/UPDATE', name, 'FAILED', str(e))
                    self.stdout.write(self.style.ERROR(f'Failed to migrate employee {fields.get("name", "Unknown")}: {str(e)}'))


            # Summary
            self.stdout.write(self.style.SUCCESS(f'\nMigration Summary:'))
            self.stdout.write(self.style.SUCCESS(f'Successfully processed: {success_count}'))
            self.stdout.write(self.style.WARNING(f'Skipped duplicates: {duplicate_count}'))
            self.stdout.write(self.style.SUCCESS('Migration completed'))