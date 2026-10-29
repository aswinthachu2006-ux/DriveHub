from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from datetime import date

class UserProfile(models.Model):
    STATUS_CHOICES = [
        ('Not Uploaded', 'Not Uploaded'),
        ('Pending', 'Pending Verification'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    ]


    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone = models.CharField(max_length=20, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    address = models.TextField(blank=True)
    
    # Licence Details
    licence_number = models.CharField(max_length=50, blank=True)
    licence_issue_date = models.DateField(null=True, blank=True)
    licence_expiry_date = models.DateField(null=True, blank=True)
    licence_image = models.ImageField(upload_to='licences/', blank=True, null=True)
    licence_status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='Not Uploaded')
    rejection_reason = models.TextField(blank=True, null=True)
    admin_notes = models.TextField(blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s Profile ({self.licence_status})"

    @property
    def rto_state(self):
        """Extracts and returns the issuing Indian State/UT from the driving licence number."""
        if not self.licence_number:
            return None
        clean = self.licence_number.replace('-', '').replace(' ', '').upper()
        if len(clean) >= 2:
            code = clean[:2]
            return self.INDIAN_STATE_CODES.get(code, f"State RTO ({code})")
        return None

    @property
    def age(self):
        if self.date_of_birth:
            today = date.today()
            return today.year - self.date_of_birth.year - (
                (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
            )
        return None

    @property
    def is_licence_valid(self):
        if self.licence_status != 'Approved':
            return False
        if self.licence_expiry_date and self.licence_expiry_date < date.today():
            return False
        return True

    def check_eligibility(self, car=None):
        """
        Rule-based eligibility checker:
        1. Checks profile completion & date of birth
        2. Checks driving licence status (must be Approved)
        3. Checks driving licence expiration
        4. Checks minimum age threshold for the selected vehicle category
        """
        if not self.date_of_birth:
            return False, "Please complete your profile with your Date of Birth."

        if self.licence_status == 'Not Uploaded':
            return False, "Indian Driving Licence not uploaded. Please submit your LMV driving licence for Parivahan / RTO verification."
        
        if self.licence_status == 'Pending':
            return False, "Your Indian Driving Licence is currently pending administrator & Parivahan verification."
        
        if self.licence_status == 'Rejected':
            reason = self.rejection_reason or "Document does not satisfy verification criteria."
            return False, f"Driving licence verification was rejected: {reason}"
        
        if self.licence_expiry_date and self.licence_expiry_date < date.today():
            return False, "Your Indian Driving Licence has expired under RTO records. Please renew and re-upload."

        min_age = 21
        category_name = "Normal"
        if car:
            min_age = getattr(car, 'minimum_age', 21)
            category_name = getattr(car, 'category', 'Standard')
        
        user_age = self.age
        if user_age is None or user_age < min_age:
            return False, f"Eligibility requirement: You must be at least {min_age} years old to rent {category_name} vehicles. (Your recorded age: {user_age or 'Unknown'})."

        return True, "Eligible to rent this vehicle."


@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
    else:
        if hasattr(instance, 'profile'):
            instance.profile.save()
