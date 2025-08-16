#!/usr/bin/env python3
"""
TaskWeave AI - Celery Worker
Run this file to start the Celery worker for background tasks
"""
import os
import sys

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from celery_app import celery
from simple_app import app

if __name__ == '__main__':
    with app.app_context():
        # Start celery worker
        celery.start()