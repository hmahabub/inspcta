import json
import os
import csv
from datetime import datetime
from django.core.management.base import BaseCommand
from vessel.models import LV  # Replace with your actual model
from clients.models import Client

class Command(BaseCommand):
    help = 'Migrate lv data with duplicate phone number handling'

    def add_arguments(self, parser):
        parser.add_argument(
            '--skip-duplicates',
            action='store_true',
            help='Skip lvs with duplicate phone numbers'
        )
        parser.add_argument(
            '--update-duplicates',
            action='store_true',
            help='Update existing lvs when phone numbers conflict'
        )

    # def load_mappings(self):
    #     pk_mapping_file_path = os.path.join(os.path.dirname(__file__), 'client_log_file.csv')

    #     # Load PK mappings for foreign keys
    #     pk_mappings = {}
    #     with open(pk_mapping_file_path) as f:
    #         reader = csv.DictReader(f)
    #         for row in reader:
    #             if row['model'] not in pk_mappings:
    #                 pk_mappings[row['model']] = {}
    #             pk_mappings[row['model']][row['old_pk']] = row['new_pk']
        
    #     return pk_mappings

    def handle(self, *args, **options):
        # pk_mappings = self.load_mappings()
        json_file_path = os.path.join(os.path.dirname(__file__), 'l_vessel.json')
        log_file_path = os.path.join(os.path.dirname(__file__), 'lv_log_file.csv')
        # keep_pks = [1,2]
        # LV.objects.exclude(pk__in=keep_pks).delete()


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
                    lvs_data = json.loads(unescaped_content)
                    
                    if isinstance(lvs_data, str):
                        lvs_data = json.loads(lvs_data)
                        
            except FileNotFoundError:
                self.stdout.write(self.style.ERROR('lvs.json file not found'))
                return
            except json.JSONDecodeError as e:
                self.stdout.write(self.style.ERROR(f'Invalid JSON format: {str(e)}'))
                return

            DEFAULT_VALUES = {

            }

            FIELD_MAPPING = {
                "vessel_name" : "name",
                "code" : "code",
                "loa" : "loa",
                "brdth"  :"brdth",
                "fb" : "fb",
                "light_fpk" : "light_fpk",
                "light_apk" : "light_apk",
            }

            FOREIGN_KEY_VALUES = {
            }

            fail_count = 0
            success_count = 0

            for lv_data in lvs_data:
                try:
                    if isinstance(lv_data, str):
                        lv_data = json.loads(lv_data)
                    
                    fields = lv_data['fields']
                    old_pk = lv_data['pk']
                    name = fields.get('vessel_name', '')

                    lv = LV()
                    for target_field, source_field in FIELD_MAPPING.items():
                        if source_field in fields:
                            value = fields[source_field]
                            setattr(lv, target_field, value)
                    
                    for field, value in DEFAULT_VALUES.items():
                        setattr(lv, field, value)

                    # for target_field, source_field in FOREIGN_KEY_VALUES.items():
                    #     old_fk = fields[source_field]
                    #     if old_fk:
                    #         model_name = source_field  # e.g., 'client'
                    #         new_fk = pk_mappings.get(model_name, {}).get(str(old_fk))
                    #         value = Client.objects.get(pk=new_fk)
                    #         if new_fk:
                    #             setattr(lv, target_field, value)
                    #         else:
                    #             raise ValueError(f"Missing FK mapping for {model_name}{old_fk}")


                    
                    lv.save()
                    log_action(old_pk, lv.pk, 'CREATE', name, 'SUCCESS')
                    success_count += 1
                    self.stdout.write(self.style.SUCCESS(f'Successfully migrated lv: {lv.code}'))
                
                except Exception as e:
                    log_action(old_pk, '', 'CREATE', name, 'FAILED', str(e))
                    fail_count += 1
                    self.stdout.write(self.style.ERROR(f'Failed to migrate lv {fields.get("code", "Unknown")}: {str(e)}'))

            # Summary
            self.stdout.write(self.style.SUCCESS(f'\nMigration Summary:'))
            self.stdout.write(self.style.SUCCESS(f'Successfully processed: {success_count}'))
            self.stdout.write(self.style.WARNING(f'Failed attempt: {fail_count}'))
            self.stdout.write(self.style.SUCCESS('Migration completed'))