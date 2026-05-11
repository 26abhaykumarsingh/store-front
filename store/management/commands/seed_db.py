import os
from django.core.management.base import BaseCommand
from django.db import connection
from pathlib import Path

class Command(BaseCommand):
  help = 'Populates the database with collections and products'

  def handle(self, *args, **options):
    print('Populating the database...')
    current_dir = os.path.dirname(__file__)
    file_path = os.path.join(current_dir, 'seed.sql')
    sql = Path(file_path).read_text(encoding='utf-8')

    with connection.cursor() as cursor:
        for statement in [s.strip() for s in sql.split(';') if s.strip()]:
            cursor.execute(statement)


    