import json
import os
import csv
from datetime import datetime
from django.core.management.base import BaseCommand
from vessel.models import LV,MV  # Replace with your actual model
from clients.models import Client

class Command(BaseCommand):
    help = 'Migrate mv data with duplicate phone number handling'

    def add_arguments(self, parser):
        parser.add_argument(
            '--skip-duplicates',
            action='store_true',
            help='Skip mvs with duplicate phone numbers'
        )
        parser.add_argument(
            '--update-duplicates',
            action='store_true',
            help='Update existing mvs when phone numbers conflict'
        )

    def load_mappings(self):
        pk_mapping_file_path = os.path.join(os.path.dirname(__file__), 'lv_log_file.csv')

        # Load PK mappings for foreign keys
        pk_mappings = {}
        with open(pk_mapping_file_path) as f:
            reader = csv.DictReader(f)
            for row in reader:
                pk_mappings[row['old_pk']] = row['new_pk']
        
        return pk_mappings

    def handle(self, *args, **options):
        # pk_mappings = self.load_mappings()
        json_file_path = os.path.join(os.path.dirname(__file__), 'm_vessel.json')
        log_file_path = os.path.join(os.path.dirname(__file__), 'mv_log_file.csv')
        # keep_pks = [1,2]
        # MV.objects.exclude(pk__in=keep_pks).delete()


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
                    mvs_data = json.loads(unescaped_content)
                    
                    if isinstance(mvs_data, str):
                        mvs_data = json.loads(mvs_data)
                        
            except FileNotFoundError:
                self.stdout.write(self.style.ERROR('mvs.json file not found'))
                return
            except json.JSONDecodeError as e:
                self.stdout.write(self.style.ERROR(f'Invalid JSON format: {str(e)}'))
                return

            DEFAULT_VALUES = {

            }

            FIELD_MAPPING = {
                
                "date" :  "date",
                "m_vessel"  : "mv",
                "co_eff"  : "co_eff",
                "consignee" :  "consignee",
                "cargo" :  "cargo",
                "survey" :  "survey",
                "shrinkage" :  "shrinkage",
                "load_fb" :  "load_fb",
                "density"  : "density",
                "cons" :  "cons",
                "quantity"  : "quantity",
                "final_quantity" :  "final_quantity",
                "tpc" :  "tpc",
                "load_fpk"  : "load_fpk",
                "load_apk" :  "load_apk",
                "forw_drft" :  "forw_drft",
                "aft_drft" :  "aft_drft",
                "mid_drft" :  "mid_drft"
            }

            FOREIGN_KEY_VALUES = {
            "l_vessel"  : "code",
            }

            fail_count = 0
            success_count = 0

            for mv_data in mvs_data:
                try:
                    if isinstance(mv_data, str):
                        mv_data = json.loads(mv_data)
                    
                    fields = mv_data['fields']
                    old_pk = mv_data['pk']
                    name = fields.get('mv', '')

                    mv = MV()
                    for target_field, source_field in FIELD_MAPPING.items():
                        if source_field in fields:
                            value = fields[source_field]
                            setattr(mv, target_field, value)

                    
                    
                    for field, value in DEFAULT_VALUES.items():
                        setattr(mv, field, value)
                    

                    for target_field, source_field in FOREIGN_KEY_VALUES.items():
                        old_fk = fields[source_field]
                        if old_fk:
                            value = LV.objects.filter(code=old_fk)[0]
                            if value:
                                setattr(mv, target_field, value)
                            else:
                                raise ValueError(f"Missing FK mapping for {old_fk}")
                    
                    mv.save()
                    log_action(old_pk, mv.pk, 'CREATE', name, 'SUCCESS')
                    success_count += 1
                    
                    self.stdout.write(self.style.SUCCESS(f'Successfully migrated mv: {mv.m_vessel}'))
                
                except Exception as e:
                    log_action(old_pk, '', 'CREATE', name, 'FAILED', str(e))
                    fail_count += 1
                    self.stdout.write(self.style.ERROR(f'Failed to migrate mv {fields.get("mv", "Unknown")}: {str(e)}'))

            # Summary
            self.stdout.write(self.style.SUCCESS(f'\nMigration Summary:'))
            self.stdout.write(self.style.SUCCESS(f'Successfully processed: {success_count}'))
            self.stdout.write(self.style.WARNING(f'Failed attempt: {fail_count}'))
            self.stdout.write(self.style.SUCCESS('Migration completed'))