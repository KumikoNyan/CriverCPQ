from django.contrib.auth.models import AbstractUser
from django.db import models

# All user parameters are under this model.
class User(AbstractUser):
    USER_TYPE_CHOICES = [
        ('OAA', 'Office of Admission and Aid'),
        ('Offices/Departments', 'Offices/Departments'),
        ('Scholar', 'Scholar'),
    ]
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES)

    # Provide custom related names for the groups and user_permissions fields
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='shims_users_groups',
        blank=True,
        verbose_name='groups',
        help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.',
    )
    # Permissions that the user has
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='shims_users_permissions',
        blank=True,
        verbose_name='user permissions',
        help_text='Specific permissions for this user.',
    )

# Scholar accounts will have these fields, and id_number is derived from the original user credentials (username)
class Scholar(models.Model):
    id_number = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        primary_key=True,
    )
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone_number = models.CharField(max_length=20)
    year = models.IntegerField()
    required_service_hours = models.IntegerField()
    total_rendered_service_hours = models.IntegerField(default=0)
    penalty_service_hours = models.IntegerField(default=0)
    total_required_service_hours = models.IntegerField()
    service_hours_status = models.CharField(max_length=20)
    term=models.CharField(max_length=300, default='Intersession') 

    def __str__(self):
        return f"{self.id_number} ({self.first_name} {self.last_name})"
    
    # def save(self, *args, **kwargs):
    #     self.total_required_service_hours = self.penalty_service_hours + self.required_service_hours - self.total_rendered_service_hours
    #     super().save(*args, **kwargs)

# Short form of Scholar Assistance Request Form, this model contains all fields for Service Hour Opportunity requests.
class SARF(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=300)
    email = models.CharField(max_length=300)
    task_name = models.CharField(max_length=300)
    task_description = models.CharField(max_length=900)
    task_mode = models.CharField(max_length=300)
    service_type = models.CharField(max_length=300)
    date = models.DateField()
    location = models.CharField(max_length=300)
    start_time = models.TimeField()
    end_time = models.TimeField()
    required_hours = models.IntegerField() 
    duration = models.CharField(max_length=300)
    skills = models.CharField(max_length=300)
    signup_link = models.URLField(max_length=900)  # Use URLField for signup_link
    scholars_needed = models.IntegerField()
    status = models.CharField(max_length=300, default='Pending')
   
    #enlisted_status=models.CharField(max_length=300, default='Pending...')
    #hours_completed=models.IntegerField(default=0)

    def __str__(self):
        return f"pk: {self.pk} - {self.name}, Task Name: {self.task_name}"
    
    def save(self, *args, **kwargs):
        # Calculate the difference in hours between end_time and start_time
        start = self.start_time.hour + self.start_time.minute / 60
        end = self.end_time.hour + self.end_time.minute / 60
        self.required_hours = round(end - start, 2)  # Round to 2 decimal places
        super().save(*args, **kwargs)


class EnlistedSHO(models.Model):
    scholar = models.ForeignKey(Scholar, on_delete=models.CASCADE)
    sarf = models.ForeignKey(SARF, on_delete=models.CASCADE)
    hours_completed = models.IntegerField()
  #  status = models.CharField(max_length=20, choices=[('complete', 'Complete'), ('incomplete', 'Incomplete')])
    enlisted_status = models.CharField(max_length=300, default='Pending')

    class Meta:
        unique_together = ('scholar', 'sarf')

    def __str__(self):
        return f"Scholar: {self.scholar}, SARF: {self.sarf}"

    def save(self, *args, **kwargs):
        # Set hours_completed to required_hours if not provided
        if self.hours_completed is None:
            self.hours_completed = self.sarf.required_hours
        super().save(*args, **kwargs)

