"""
Celery configuration and setup for background image processing tasks.
"""
import os
from celery import Celery
from config.settings import settings

# Get Redis URL from settings
redis_url = getattr(settings, 'REDIS_URL', 'redis://localhost:6379/0')

# Create Celery instance
celery_app = Celery(
    "filecraft",
    broker=redis_url,
    backend=redis_url,
    include=[
        "app.tasks.image_tasks",
        "app.tasks.audio_tasks",
        "app.tasks.video_tasks",
        "app.tasks.optimization_tasks"
    ]
)

# Celery configuration
celery_app.conf.update(
    # Task routing
    task_routes={
        "app.tasks.image_tasks.*": {"queue": "image_processing"},
        "app.tasks.audio_tasks.*": {"queue": "audio_processing"},
        "app.tasks.video_tasks.*": {"queue": "video_processing"},
        "app.tasks.optimization_tasks.*": {"queue": "optimization"},
    },
    
    # Task serialization
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    
    # Task execution
    task_always_eager=False,
    task_eager_propagates=True,
    task_ignore_result=False,
    task_store_eager_result=True,
    
    # Worker configuration
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
    worker_disable_rate_limits=False,
    
    # Task result expiration
    result_expires=3600,  # 1 hour
    
    # Task priorities
    task_inherit_parent_priority=True,
    task_default_priority=5,
    
    # Memory and resource limits
    worker_max_memory_per_child=512000,  # 512MB
    task_soft_time_limit=300,  # 5 minutes
    task_time_limit=600,  # 10 minutes
    
    # Optimization settings
    task_compression="gzip",
    result_compression="gzip",
    
    # Monitoring
    worker_send_task_events=True,
    task_send_sent_event=True,
    
    # Queue configuration
    task_default_queue="default",
    task_queue_max_priority=10,
    
    # Beat schedule for cleanup tasks
    beat_schedule={
        "cleanup-temp-files": {
            "task": "app.tasks.optimization_tasks.cleanup_temp_files",
            "schedule": 3600.0,  # Every hour
        },
    },
)

# Queue definitions
celery_app.conf.task_routes = {
    "app.tasks.image_tasks.convert_image_async": {"queue": "image_processing"},
    "app.tasks.image_tasks.resize_image_async": {"queue": "image_processing"},
    "app.tasks.image_tasks.optimize_image_async": {"queue": "optimization"},
    "app.tasks.image_tasks.batch_convert_images": {"queue": "batch_processing"},
    "app.tasks.audio_tasks.convert_audio_async": {"queue": "audio_processing"},
    "app.tasks.audio_tasks.batch_convert_audio": {"queue": "batch_processing"},
    "app.tasks.audio_tasks.extract_audio_features_async": {"queue": "audio_processing"},
    "app.tasks.audio_tasks.apply_audio_effects_async": {"queue": "audio_processing"},
    "app.tasks.video_tasks.convert_video_task": {"queue": "video_processing"},
    "app.tasks.video_tasks.batch_convert_videos_task": {"queue": "batch_processing"},
    "app.tasks.video_tasks.extract_audio_task": {"queue": "video_processing"},
    "app.tasks.video_tasks.generate_thumbnail_task": {"queue": "video_processing"},
    "app.tasks.optimization_tasks.*": {"queue": "optimization"},
}

if __name__ == "__main__":
    celery_app.start()