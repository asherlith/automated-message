import os
from datetime import timedelta
from celery import Celery

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'automate_mail.settings')

app = Celery('automate_mail')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()

app.conf.beat_schedule = {
    # any name can be chosen
    'send-nice-mail': {
        # where the task is located
        'task': 'mail.tasks.send_many_email',
        # when it will execute
        "schedule": timedelta(days=1),
        # arguments passed into the task function
        'args': ({"email_subject": "bday", "email_body": "don't forget my bday"},)
    },

    'send-nice-message': {
        # where the task is located
        'task': 'mail.tasks.send_many_message',
        # when it will execute
        "schedule": timedelta(days=1),
        # arguments passed into the task function
        'args': ({"body": "don't forget my bday"},)
    }
}


@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
