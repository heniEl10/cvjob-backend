from django.conf import settings
from rest_framework import serializers
from .models import Resume, CustomUser, JobPosting, Application, Blog


class CandidateSerializer(serializers.ModelSerializer):
    resume = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'name', 'role', 'resume']
        read_only_fields = ['role']

    def get_resume(self, obj):
        try:
            return ResumeSerializer(obj.resume).data
        except Resume.DoesNotExist:
            return None


class ResumeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resume
        fields = '__all__'
        read_only_fields = ['user']


class RecruiterSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'name', 'role', 'company', 'position']
        read_only_fields = ['role']


class JobPostingSerializer(serializers.ModelSerializer):
    company_logo = serializers.SerializerMethodField()
    class Meta:
        model = JobPosting
        fields = ['id', 'title', 'description', 'type', 'city', 'created_on', 'status', 'company', 'category', 'company_logo', 'number_of_candidates']
        read_only_fields = ['recruiter']

    def get_company_logo(self, obj):
        if obj.company_logo:
            return f"{settings.BASE_URL}{obj.company_logo.url}"
        return None


class ApplicationSerializer(serializers.ModelSerializer):
    resume = serializers.SerializerMethodField(source='candidate.resume')
    job_title = serializers.SerializerMethodField(source='job.title')
    candidate_name = serializers.SerializerMethodField(source='candidate.name')
    candidate_email = serializers.SerializerMethodField(source='candidate.email')

    class Meta:
        model = Application
        fields = ['id', 'resume', 'job_title', 'candidate_name', 'candidate_email', 'status', 'applied_on']
        read_only_fields = ['job', 'status']

    def get_resume(self, obj):
        try:
            return ResumeSerializer(obj.candidate.resume).data
        except Resume.DoesNotExist:
            return None

    def get_job_title(self, obj):
        return obj.job.title

    def get_candidate_name(self, obj):
        return obj.candidate.name

    def get_candidate_email(self, obj):
        return obj.candidate.email


class BlogSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source='author.name')
    excerpt = serializers.SerializerMethodField()
    thumbnail = serializers.SerializerMethodField()

    class Meta:
        model = Blog
        fields = ['id', 'title', 'content', 'slug', 'thumbnail', 'created_at', 'updated_at', 'author', 'excerpt']
        read_only_fields = ['slug', 'created_at', 'updated_at']

    def get_excerpt(self, obj):
        return obj.content[:160]

    def get_thumbnail(self, obj):
        if obj.thumbnail:
            return f"{settings.BASE_URL}{obj.thumbnail.url}"
        return None

