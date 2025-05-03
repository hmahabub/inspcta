import json
import os
import csv
from datetime import datetime
from django.core.management.base import BaseCommand
from books.models import CashBook  # Replace with your actual model
from decimal import Decimal

class Command(BaseCommand):
    help = 'Migrate cash_book data with duplicate phone number handling'

    def add_arguments(self, parser):
        parser.add_argument(
            '--skip-duplicates',
            action='store_true',
            help='Skip cash_books with duplicate phone numbers'
        )
        parser.add_argument(
            '--update-duplicates',
            action='store_true',
            help='Update existing cash_books when phone numbers conflict'
        )

    def handle(self, *args, **options):
        json_file_path = os.path.join(os.path.dirname(__file__), 'cash_book.json')
        log_file_path = os.path.join(os.path.dirname(__file__), 'cash_book_log_file.csv')
        # keep_pks = [1,2]
        # CashBook.objects.exclude(pk__in=keep_pks).delete()


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
                    cash_books_data = json.loads(unescaped_content)
                    
                    if isinstance(cash_books_data, str):
                        cash_books_data = json.loads(cash_books_data)
                        
            except FileNotFoundError:
                self.stdout.write(self.style.ERROR('cash_books.json file not found'))
                return
            except json.JSONDecodeError as e:
                self.stdout.write(self.style.ERROR(f'Invalid JSON format: {str(e)}'))
                return

            DEFAULT_VALUES = {

            }

            FIELD_MAPPING = {
                "date" : "date",
                "particulars" : "prt",
                "transaction_type" : "cord",
                "amount" : "amount"
            }

            FOREIGN_KEY_VALUES = {
            }

            fail_count = 0
            success_count = 0
            current_balance = 0
            
            for cash_book_data in cash_books_data:
                try:
                    if isinstance(cash_book_data, str):
                        cash_book_data = json.loads(cash_book_data)
                    
                    fields = cash_book_data['fields']
                    old_pk = cash_book_data['pk']
                    name = fields.get('prt', '')
                    cord = fields.get('cord')

                    cash_book = CashBook()
                    for target_field, source_field in FIELD_MAPPING.items():
                        if source_field in fields:
                            value = fields[source_field]
                            setattr(cash_book, target_field, value)
                    for field, value in DEFAULT_VALUES.items():
                        setattr(cash_book, field, value)

                    if cord == 'DEBIT':
                        current_balance = current_balance - Decimal(cash_book.amount)
                    elif cord == 'CREDIT':
                        current_balance = current_balance + Decimal(cash_book.amount)

                    setattr(cash_book, "current_balance", current_balance)

                    cash_book.save()
                    log_action(old_pk, cash_book.pk, 'CREATE', name, 'SUCCESS')
                    success_count += 1
                    self.stdout.write(self.style.SUCCESS(f'Successfully migrated cash_book: {cash_book.particulars}'))
                
                except Exception as e:
                    log_action(old_pk, '', 'CREATE', name, 'FAILED', str(e))
                    fail_count += 1
                    self.stdout.write(self.style.ERROR(f'Failed to migrate cash_book {fields.get("prt", "Unknown")}: {str(e)}'))

            # Summary
            self.stdout.write(self.style.SUCCESS(f'\nMigration Summary:'))
            self.stdout.write(self.style.SUCCESS(f'Successfully processed: {success_count}'))
            self.stdout.write(self.style.WARNING(f'Failed attempt: {fail_count}'))
            self.stdout.write(self.style.SUCCESS('Migration completed'))