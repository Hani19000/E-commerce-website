#!/usr/bin/env python
import os
import sys
import time
import django
from django.conf import settings
from django.db import connections
from django.db.utils import OperationalError

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecom.settings')
django.setup()

def wait_for_database():
    """Wait for database to be ready"""
    db_conn = connections['default']
    while True:
        try:
            cursor = db_conn.cursor()
            cursor.execute("SELECT 1")
            cursor.close()
            print("Database is ready!")
            break
        except OperationalError:
            print("Waiting for database...")
            time.sleep(5)

if __name__ == "__main__":
    wait_for_database()
