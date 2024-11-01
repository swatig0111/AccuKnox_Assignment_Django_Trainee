from django.db import models, transaction
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.management.base import BaseCommand
from django.db import IntegrityError

# Models
class Account(models.Model):
    name = models.CharField(max_length=100)
    balance = models.DecimalField(max_digits=10, decimal_places=2)
    version = models.IntegerField(default=1, unique=True)  # Used to force integrity errors

class TransactionLog(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    action = models.CharField(max_length=100)
    status = models.CharField(max_length=20)

# Signal handler that will try to create a log entry
@receiver(post_save, sender=Account)
def log_account_change(sender, instance, created, **kwargs):
    TransactionLog.objects.create(
        account=instance,
        action="account_created" if created else "account_updated",
        status="success"
    )
    
    # Force an integrity error by trying to create another account with same version
    Account.objects.create(
        name="Duplicate Version Account",
        balance=0,
        version=instance.version  # This will cause an IntegrityError
    )

class Command(BaseCommand):
    def handle(self, *args, **options):
        # Test 1: Without explicit transaction
        print("\nTest 1: Implicit Transaction Behavior")
        try:
            # This creation will trigger the signal
            account1 = Account.objects.create(
                name="Test Account 1",
                balance=1000,
                version=1
            )
            print("❌ If you see this, transactions are not shared (shouldn't reach here)")
        except IntegrityError:
            print("✅ IntegrityError caught - no account or log created (proving shared transaction)")
            
        # Verify no records were created
        print(f"Accounts count: {Account.objects.count()} (should be 0)")
        print(f"Logs count: {TransactionLog.objects.count()} (should be 0)")

        # Test 2: With explicit transaction
        print("\nTest 2: Explicit Transaction Behavior")
        try:
            with transaction.atomic():
                account2 = Account.objects.create(
                    name="Test Account 2",
                    balance=2000,
                    version=2
                )
                print("❌ If you see this, transactions are not shared (shouldn't reach here)")
        except IntegrityError:
            print("✅ IntegrityError caught - no account or log created (proving shared transaction)")
            
        # Verify no records were created
        print(f"Accounts count: {Account.objects.count()} (should be 0)")
        print(f"Logs count: {TransactionLog.objects.count()} (should be 0)")

        # Test 3: Successful transaction without forced error
        print("\nTest 3: Successful Transaction (without forced error)")
        @receiver(post_save, sender=Account)
        def successful_log(sender, instance, created, **kwargs):
            TransactionLog.objects.create(
                account=instance,
                action="successful_creation",
                status="success"
            )
            
        try:
            with transaction.atomic():
                account3 = Account.objects.create(
                    name="Test Account 3",
                    balance=3000,
                    version=3
                )
            print("✅ Transaction completed successfully")
            print(f"Accounts count: {Account.objects.count()} (should be 1)")
            print(f"Logs count: {TransactionLog.objects.count()} (should be 1)")
        except IntegrityError:
            print("❌ Unexpected error")