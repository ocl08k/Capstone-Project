from django.db import models
from django.contrib.auth.models import User
from dotenv import load_dotenv
import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

load_dotenv()

# Email Notification via Twilio API
# https://app.sendgrid.com/guide/integrate/langs/python
class Email_report(models.Model):
    result = models.PositiveIntegerField()   # result mark
    
    def __str__(self):
        return str(self.result)
    
    def save(self, *args, **kwargs):
        # condition MUST BE CHANGED
        if self.result < 50:
            message = Mail(
                from_email='from@emaildomain.com',
                to_emails='to@emaildomain.com',
                subject="Weekly Report on your child's Performance",
                html_content='<strong>and easy to do anywhere, even with Python</strong>')
            try:
                sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))  # hidden API_KEY for security
                response = sg.send(message)
                print(response.status_code)
                print(response.body)
                print(response.headers)
            except Exception as e:
                print(e.message)
            
        return super().save(*args, **kwargs)

class UserProfile(models.Model):
    """User profile to store additional information related to users"""
    
    ROLE_CHOICES = [
        ('parent', 'Parent'),         # Parent profile
        ('child', 'Child'),           # Child profile
        ('therapist', 'Therapist'),   # Therapist profile
    ]

    # Link UserProfile to Django's built-in User model
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)  # Role-based permission
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    avatar_id = models.PositiveIntegerField(null=True, blank=True)  # Field to store avatar ID
    customized_username = models.CharField(max_length=50, blank=True, null=True)  # Field to store customerized username
    date_of_birth = models.DateField(blank=True, null=True)

    # Optional field to store parent-child relationship directly
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, blank=True, null=True, related_name='children')
    
    def __str__(self):
        return f"{self.user.username} - {self.get_role_display()}"

    @property
    def email(self):
        '''Retrieve email from the User model.'''
        return self.user.email

    @property
    def username(self):
        '''Retrieve username from the User model.'''
        return self.user.username

    @property
    def user_id(self):
        '''Retrieve user ID from the User model.'''
        return self.user.id

@receiver(post_save, sender=User)
def create_or_save_user_profile(sender, instance, created, **kwargs):
    """Create or save UserProfile for each User"""
    if created:
        UserProfile.objects.create(user=instance)
    else:
        instance.profile.save()

# Relationships according to the ER model v1
# Using Separate Model (i.e new table) as a separate model
class ParentChildRelation(models.Model):
    parent = models.ForeignKey(User, related_name='parent_children_relations', on_delete=models.CASCADE)
    child = models.OneToOneField(User, related_name='child_parent_relation', on_delete=models.CASCADE)
    child_name = models.CharField(max_length=100)
    child_icon = models.ImageField(upload_to='child_icons/', blank=True, null=True)

    def __str__(self):
        return f"{self.child_name} (Child of {self.parent.username})"

# Relationships according to the ER model v1
# Using Separate Model (i.e new table) for managing the request and approval process
class ParentChildRequest(models.Model):
    child = models.ForeignKey(User, related_name='sent_parent_requests', on_delete=models.CASCADE)
    parent = models.ForeignKey(User, related_name='received_child_requests', on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=[('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected')], default='pending')

    def __str__(self):
        return f"Request from {self.child.username} to {self.parent.username} - {self.status}"

# Relationships according to the ER model v1
# Using Separate Model (i.e new table) as a separate model
class TherapistChildRelation(models.Model):
    '''
    start_date: A date field that records when the therapist-child relationship was established
    notes: An optional field for any notes or specific details about the relationship
    '''
    therapist = models.ForeignKey(User, related_name='patients', on_delete=models.CASCADE)
    child = models.OneToOneField(User, related_name='therapist_relation', on_delete=models.CASCADE)
    child_name = models.CharField(max_length=100)
    child_icon = models.ImageField(upload_to='child_icons/', blank=True, null=True)

    def __str__(self):
        return f"Child: {self.child_name} (Treated by {self.therapist.username})"

# Relationships according to the ER model v1
# Using Separate Model (i.e new table) for managing the request and approval process
class TherapistChildRequest(models.Model):
    '''
    This model manages the request and approval process, allowing therapists to request a relationship with a child. 
    The status field indicates whether the request is pending, approved, or rejected. 
    '''
    
    therapist = models.ForeignKey(User, related_name='child_requests', on_delete=models.CASCADE)
    child = models.ForeignKey(User, related_name='therapist_requests', on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=[('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected')], default='pending')
    request_date = models.DateTimeField(auto_now_add=True,
                                        help_text="A date field to record when the request was made.")
    response_date = models.DateTimeField(null=True, blank=True,
                                         help_text="A date field for when the request was approved or rejected. This field can remain blank if the status is still pending.")
    message = models.TextField(blank=True, null=True,
                               help_text="An optional field for any message or additional context the therapist wants to include with the request.")

    def __str__(self):
        return f"Request from {self.therapist.username} to treat {self.child.username} - {self.status}"

class Note(models.Model):
    title = models.CharField(max_length=100)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notes")
    def __str__(self):
        return self.title

# Entity according to the ER model v1
class AIChatbot(models.Model):
    name = models.CharField(max_length=100, 
                            help_text="Represents the name of the chatbot.")
    icon_picture = models.ImageField(upload_to='chatbot_icons/', blank=True, null=True,
                                     help_text="An optional field to store an icon image for the chatbot.")
    theme = models.CharField(max_length=50, 
                             help_text="A field to describe the theme or style of the chatbot (e.g., friendly, formal).")

    def __str__(self):
        return self.name

    
