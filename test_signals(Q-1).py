from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
import time
from django.core.management.base import BaseCommand

# Model
class Person(models.Model):
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

# Signal handler that deliberately sleeps to demonstrate blocking
@receiver(post_save, sender=Person)
def long_running_handler(sender, instance, created, **kwargs):
    print(f"Signal handler started at: {time.strftime('%H:%M:%S')}")
    time.sleep(5)  # Simulate long-running task
    print(f"Signal handler finished at: {time.strftime('%H:%M:%S')}")

# Management command to demonstrate the behavior
class Command(BaseCommand):
    def handle(self, *args, **options):
        print(f"Starting person creation at: {time.strftime('%H:%M:%S')}")
        
        # Create a person which will trigger the signal
        person = Person.objects.create(name="Test Person")
        
        print(f"Person creation completed at: {time.strftime('%H:%M:%S')}")
        print("If you see this message before the signal handler finished, signals are async")
        print("If you see this message after the signal handler finished, signals are sync")