import json
import os
import csv
from datetime import datetime
from django.core.management.base import BaseCommand
from projects.models import Project  # Replace with your actual model
from clients.models import Client
from employees.models import Employee
from sales.models import Sale, Task


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
        json_file_path = os.path.join(os.path.dirname(__file__), 'sale.json')
        log_file_path = os.path.join(os.path.dirname(__file__), 'sale_log_file.csv')
        # keep_pks = [1,2]
        # Sale.objects.exclude(pk__in=keep_pks).delete()


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
                    'model' : 'Sale',
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
                self.stdout.write(self.style.ERROR('sales.json file not found'))
                return
            except json.JSONDecodeError as e:
                self.stdout.write(self.style.ERROR(f'Invalid JSON format: {str(e)}'))
                return

            DEFAULT_VALUES = {}

            FIELD_MAPPING = {
                "currency":  "currency",
                "invoice_no" : "invoice_no",
                "invoice_date":  "invoice_date",
                "report_no":  "report_no",
                "report_date":  "report_date",
                "job_order_no" : "job_order_no",
                "shipper":  "shipper",
                "buyer":  "buyer",
                "cargo":  "cargo",
                "bl_qtn":  "bl_qtn",
                "ins_qtn":  "ins_qtn",
                "date_of_ins" : "date_of_ins",
                "plc_of_ins" : "plc_of_ins",
                "recieved_amount" : "recieved" 
            }

            FOREIGN_KEY_VALUES = {
                'project' : 'job',
            }
            fail_count = 0
            success_count = 0
            processed_invoice_no = set()
            counter = 0
            for exp_data in exps_data:
                try:
                    if isinstance(exp_data, str):
                        exp_data = json.loads(exp_data)
                    
                    fields = exp_data['fields']
                    old_pk = exp_data['pk']
                    name = fields.get('job', '')
                    invoice_no = fields.get('invoice_no', '')

                    if invoice_no in processed_invoice_no:
                        invoice_no = invoice_no + "-C"+str(counter)
                        counter +=1

                    # Create new project
                    exp = Sale()
                    for target_field, source_field in FIELD_MAPPING.items():
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
                    task_instance = {
                    "task1_desc" : "task1_cost",
                    "task2_desc" : "task2_cost",
                    "task3_desc" : "task3_cost",
                    "task4_desc" : "task4_cost",
                    "task5_desc" : "task5_cost",
                    "task6_desc" : "task6_cost",
                    "task7_desc" : "task7_cost",
                    }

                    for desc, cost in task_instance.items():
                        desc_value = fields.get(desc, "") or ""
                        cost_value = fields.get(cost, 0) or 0
                        if not (desc_value == "" and cost_value == 0):
                            t = Task()
                            setattr(t, 'sale', exp)
                            setattr(t, "description", desc_value)
                            setattr(t, "cost", cost_value)
                            t.save()
                    log_action(old_pk, exp.pk, 'CREATE', name, 'SUCCESS')
                    success_count += 1
                    processed_invoice_no.add(invoice_no)
                    self.stdout.write(self.style.SUCCESS(f'Successfully migrated sales: {old_pk}'))
                
                except Exception as e:
                    log_action( old_pk, '', 'CREATE', name, 'FAILED', str(e))
                    fail_count += 1
                    self.stdout.write(self.style.ERROR(f'Failed to migrate sales {fields.get("old_pk", "Unknown")}: {str(e)}'))

            # Summary
            self.stdout.write(self.style.SUCCESS(f'\nMigration Summary:'))
            self.stdout.write(self.style.SUCCESS(f'Successfully processed: {success_count}'))
            self.stdout.write(self.style.WARNING(f'Failed attempt: {fail_count}'))
            self.stdout.write(self.style.SUCCESS('Migration completed'))