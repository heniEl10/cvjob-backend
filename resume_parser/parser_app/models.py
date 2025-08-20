from django.db import models
from django import forms
from django.forms import ClearableFileInput

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone
from django.utils.text import slugify


class CustomUserManager(BaseUserManager):
    def create_user(self, email, name, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, name=name, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', CustomUser.ADMIN)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, name, password, **extra_fields)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    ADMIN = 'ADMIN'
    RECRUITER = 'RECRUITER'
    CANDIDATE = 'CANDIDATE'

    ROLE_CHOICES = [
        (ADMIN, 'Admin'),
        (RECRUITER, 'Recruiter'),
        (CANDIDATE, 'Candidate'),
    ]

    email = models.EmailField('email address', unique=True)
    name = models.CharField(max_length=150)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default=CANDIDATE)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(default=timezone.now)

    # Recruiters attributes
    company = models.CharField(max_length=255, blank=True, null=True)
    position = models.CharField(max_length=255, blank=True, null=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    def __str__(self):
        return self.email

    def is_admin(self):
        return self.role == self.ADMIN

    def is_recruiter(self):
        return self.role == self.RECRUITER

    def is_candidate(self):
        return self.role == self.CANDIDATE


class Resume(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='resume', null=True, blank=True)
    resume = models.FileField('Upload Resumes', upload_to='resumes/', null=True, blank=True)
    name = models.CharField('Name', max_length=255, null=True, blank=True)
    email = models.EmailField('Email', max_length=255, null=True, blank=True)
    mobile_number = models.CharField('Mobile Number', max_length=255, null=True, blank=True)
    education = models.CharField('Education', max_length=255, null=True, blank=True)
    skills = models.CharField('Skills', max_length=1000, null=True, blank=True)
    experience = models.CharField('Experience', max_length=1000, null=True, blank=True)
    uploaded_on = models.DateTimeField('Uploaded On', auto_now_add=True)

    def __str__(self):
        return f"{self.user.name}'s Resume" if self.user else "Unassigned Resume"


class UploadResumeModelForm(forms.ModelForm):
    class Meta:
        model = Resume
        fields = ['resume']
        widgets = {
            'resume': ClearableFileInput(attrs={'multiple': True}),
        }

# delete the resume files associated with each object or record
# @receiver(post_delete, sender=Resume)
# def submission_delete(sender, instance, **kwargs):
#     instance.resume.delete(False)


class JobPosting(models.Model):
    recruiter = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='job_postings')
    title = models.CharField('Title', max_length=255)
    description = models.TextField('Description')
    type = models.CharField('Type', max_length=255, null=True, blank=True)
    city = models.CharField('City', max_length=255, null=True, blank=True)
    created_on = models.DateTimeField('Created On', auto_now_add=True)
    status = models.BooleanField('Status', default=True)
    category = models.CharField(max_length=100, null=True, blank=True)
    company = models.CharField(max_length=255, blank=True, null=True)
    company_logo = models.ImageField(upload_to='company_logos/', null=True, blank=True)
    number_of_candidates = models.IntegerField('Number of Candidates', default=1)

    def __str__(self):
        return self.title


class Application(models.Model):
    PENDING = 'PE'
    ACCEPTED = 'AC'
    REJECTED = 'RE'
    STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (ACCEPTED, 'Accepted'),
        (REJECTED, 'Rejected'),
    ]

    job = models.ForeignKey(JobPosting, on_delete=models.CASCADE, related_name='applications')
    candidate = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='applications')
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE, related_name='applications')
    applied_on = models.DateTimeField('Applied On', auto_now_add=True)
    status = models.CharField(max_length=2, choices=STATUS_CHOICES, default=PENDING)

    def __str__(self):
        return f"{self.candidate.name}'s application for {self.job.title}"


class Blog(models.Model):
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE, limit_choices_to={'role': CustomUser.ADMIN})
    title = models.CharField(max_length=200)
    content = models.TextField()
    slug = models.SlugField(max_length=200, unique=True)
    thumbnail = models.ImageField(upload_to='blog_thumbnails/', null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-created_at']