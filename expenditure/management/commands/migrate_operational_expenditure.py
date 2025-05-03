import json
import os
import csv
from datetime import datetime
from django.core.management.base import BaseCommand
from projects.models import Project  # Replace with your actual model
from clients.models import Client
from employees.models import Employee
from expenditure.models import OperationalExpenditure


class Command(BaseCommand):
    help = 'Migrate operation expenditure data with duplicate phone number handling'

    def add_arguments(self, parser):
        parser.add_argument(
            '--skip-duplicates',
            action='store_true',
            help='Skip projects with duplicate phone numbers'
        )
        parser.add_argument(
            '--update-duplicates',
            action='store_true',
            help='Update existing projects when phone numbers conflict'
        )

    def load_mappings(self):
        project_pk_mapping_file_path = os.path.join(os.path.dirname(__file__), 'project_log_file.csv')
        # Load PK mappings for foreign keys
        project_pk_mappings = {}
        with open(project_pk_mapping_file_path) as f:
            reader = csv.DictReader(f)
            for row in reader:
                project_pk_mappings[row['old_pk']] = row['new_pk']
        
        return project_pk_mappings

    def handle(self, *args, **options):
        project_pk_mappings = self.load_mappings()
        json_file_path = os.path.join(os.path.dirname(__file__), 'operation_expense.json')
        log_file_path = os.path.join(os.path.dirname(__file__), 'expenditure_operation_log_file.csv')


        with open(log_file_path, 'w', newline='') as csvfile:
            fieldnames = [
                'timestamp', 
                'model',
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
                    'model' : 'OperationalExpenditure',
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
                    exps_data = json.loads(unescaped_content)
                    
                    if isinstance(exps_data, str):
                        exps_data = json.loads(exps_data)
                        
            except FileNotFoundError:
                self.stdout.write(self.style.ERROR('operation_expense.json file not found'))
                return
            except json.JSONDecodeError as e:
                self.stdout.write(self.style.ERROR(f'Invalid JSON format: {str(e)}'))
                return

            DEFAULT_VALUES = {
                'expenditure_type': 'REGULAR',
                'payment_method' : 'CASH',
                'receipt_number' : '',

            }

            FIELD_MAPPING = {
                "escort": "escort",
                "mariner": "mariner",
                "equipment" :"equipment",
                "speedboat" :"speedboat",
                "others": "others",
                "date" : "month",
            }

            FOREIGN_KEY_VALUES = {
                'project' : 'job',
            }
            fail_count = 0
            success_count = 0

            for exp_data in exps_data:
                try:
                    if isinstance(exp_data, str):
                        exp_data = json.loads(exp_data)
                    
                    fields = exp_data['fields']
                    old_pk = exp_data['pk']
                    name = fields.get('job', '')


                    # Create new project
                    exp = OperationalExpenditure()
                    for target_field, source_field in FIELD_MAPPING.items():
                        if source_field == 'month':
                            value = fields[source_field] + '-01'
                            setattr(exp, target_field, value)
                        elif source_field in fields:
                            value = fields[source_field]
                            setattr(exp, target_field, value)
                    
                    for field, value in DEFAULT_VALUES.items():
                        setattr(exp, field, value)

                    for target_field, source_field in FOREIGN_KEY_VALUES.items():
                        old_fk = fields[source_field]
                        if old_fk:
                            model_name = source_field  # e.g., 'client'
                            if model_name == 'job':
                                new_fk = project_pk_mappings.get(str(old_fk))
                                value = Project.objects.get(pk=new_fk)

                            if new_fk:
                                setattr(exp, target_field, value)
                            else:
                                raise ValueError(f"Missing FK mapping for {model_name}{old_fk}")


                    
                    exp.save()
                    log_action(old_pk, exp.pk, 'CREATE', name, 'SUCCESS')
                    success_count += 1
                    self.stdout.write(self.style.SUCCESS(f'Successfully migrated expense: {old_pk}'))
                
                except Exception as e:
                    log_action( old_pk, '', 'CREATE', name, 'FAILED', str(e))
                    fail_count += 1
                    self.stdout.write(self.style.ERROR(f'Failed to migrate expense {fields.get("job", "Unknown")}: {str(e)}'))

            # Summary
            self.stdout.write(self.style.SUCCESS(f'\nMigration Summary:'))
            self.stdout.write(self.style.SUCCESS(f'Successfully processed: {success_count}'))
            self.stdout.write(self.style.WARNING(f'Failed attempt: {fail_count}'))
            self.stdout.write(self.style.SUCCESS('Migration completed'))