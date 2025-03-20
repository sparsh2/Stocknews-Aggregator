import os
from celery import Celery
from celery.schedules import crontab

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# Create the Celery app
app = Celery('stocknews')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()

# Configure Celery Beat schedule
app.conf.beat_schedule = {
    'ingest-news-every-hour': {
        'task': 'apps.news.tasks.ingest_news_from_sources',
        'schedule': crontab(minute=0),  # Run at the start of every hour
    },
    'cleanup-old-articles-daily': {
        'task': 'apps.news.tasks.cleanup_old_articles',
        'schedule': crontab(hour=0, minute=0),  # Run at midnight
    },
    'reprocess-failed-articles-every-6-hours': {
        'task': 'apps.news.tasks.reprocess_failed_articles',
        'schedule': crontab(hour='*/6'),  # Run every 6 hours
    },
}

@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f'Request: {self.request!r}') 