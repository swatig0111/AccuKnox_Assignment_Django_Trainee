from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.management.base import BaseCommand
import threading
import time

class Person(models.Model):
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)


thread_tracker = {}

@receiver(post_save, sender=Person)
def track_signal_thread(sender, instance, created, **kwargs):
    current_thread = threading.current_thread()
    thread_tracker['signal_handler'] = {
        'thread_id': current_thread.ident,
        'thread_name': current_thread.name,
        'timestamp': time.strftime('%H:%M:%S')
    }
    print(f"Signal handler running in thread: {current_thread.ident} ({current_thread.name})")

class Command(BaseCommand):
    def handle(self, *args, **options):
        #We can Track the main thread info
        current_thread = threading.current_thread()
        thread_tracker['main_thread'] = {
            'thread_id': current_thread.ident,
            'thread_name': current_thread.name,
            'timestamp': time.strftime('%H:%M:%S')
        }
        print(f"Main code running in thread: {current_thread.ident} ({current_thread.name})")

        # Created a separate thread to create a Person
        def create_person_in_thread():
            current_thread = threading.current_thread()
            thread_tracker['creator_thread'] = {
                'thread_id': current_thread.ident,
                'thread_name': current_thread.name,
                'timestamp': time.strftime('%H:%M:%S')
            }
            print(f"Person creation running in thread: {current_thread.ident} ({current_thread.name})")
            Person.objects.create(name="Test Person")

        # Now will Create person in main thread
        print("\nTest 1: Creating person in main thread")
        Person.objects.create(name="Main Thread Person")
        print("Main thread ID matches signal handler thread ID:", 
              thread_tracker['main_thread']['thread_id'] == thread_tracker['signal_handler']['thread_id'])

        # Here Create person in separate thread
        print("\nTest 2: Creating person in separate thread")
        thread = threading.Thread(target=create_person_in_thread, name="CustomThread")
        thread.start()
        thread.join()
        print("Creator thread ID matches signal handler thread ID:", 
              thread_tracker['creator_thread']['thread_id'] == thread_tracker['signal_handler']['thread_id'])

        # Let's Print detailed thread information
        print("\nDetailed Thread Information:")
        print(f"Main Thread: {thread_tracker['main_thread']}")
        print(f"Creator Thread: {thread_tracker['creator_thread']}")
        print(f"Signal Handler: {thread_tracker['signal_handler']}")