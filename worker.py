#!/usr/bin/env python3
"""
Celery worker script for image processing tasks.
"""
import os
import sys

# Add project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from app.celery_app import celery_app

if __name__ == "__main__":
    # Run celery worker
    celery_app.worker_main(
        [
            "worker",
            "--loglevel=info",
            "--concurrency=4",
            "--pool=threads",
            "--queues=default,image_processing,audio_processing,optimization,batch_processing",
        ]
    )
