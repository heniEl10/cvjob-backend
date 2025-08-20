"""resume_parser.parser_app URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
# from . import views
from . import admin_views, home_views, application_views, candidate_views
from django.conf import settings
from django.conf.urls.static import static
from .api import ResumeUploadView, AdminStatsView, CVRegistrationRateView, RecruiterStatsView, CandidateStatsView, ApplicationRateView
from .auth_views import LoginView, RecruiterRegisterView, CandidateRegisterView, RequestPasswordResetView, ResetPasswordView
# from .auth_views import RegisterView

router = DefaultRouter()
router.register(r'api/v1/admin/candidates', admin_views.AdminCandidateViewSet)
router.register(r'api/v1/admin/recruiters', admin_views.AdminRecruiterViewSet, basename='admin-recruiters')
router.register(r'api/v1/admin/resumes', admin_views.AdminResumeViewSet)
router.register(r'api/v1/admin/jobs', admin_views.AdminJobPostingViewSet, basename='admin-jobs')
router.register(r'api/v1/recruiter/jobs', admin_views.RecruiterJobPostingViewSet, basename='recruiter-jobs')
router.register(r'api/v1/applications', application_views.ApplicationViewSet)
router.register(r'api/v1/candidate', candidate_views.CandidateViewSet, basename='candidate')
router.register(r'api/v1/blog', home_views.BlogViewSet, basename='blog')
# GET /candidate/my_resume/ - View the candidate's resume
# PUT/PATCH /candidate/my_resume/ - Update the candidate's resume
# GET /candidate/download/ - Download the candidate's resume
# GET /candidate/list_jobs/ - View all available jobs
# POST /candidate/apply/{job_id}/ - Apply for a specific job
# GET /candidate/list_applications/ - View all the candidate's job applications


urlpatterns = [
    # path('', views.homepage, name='homepage'),
    # path('api/v1/auth/signup/', RegisterView.as_view(), name='register'),
    path('api/v1/admin/resumes/upload/', ResumeUploadView.as_view(), name='upload-resumes'),
    path('api/v1/auth/signup/recruiter/', RecruiterRegisterView.as_view(), name='recruiter-register'),
    path('api/v1/auth/signup/candidate/', CandidateRegisterView.as_view(), name='candidate-register'),
    path('api/v1/auth/signin/', LoginView.as_view(), name='login'),
    path('api/password/email/', RequestPasswordResetView.as_view(), name='request_password_reset'),
    path('api/password/reset/', ResetPasswordView.as_view(), name='reset_password'),
    path('api/v1/admin/stats/', AdminStatsView.as_view(), name='stats'),
    path('api/v1/recruiter/stats/', RecruiterStatsView.as_view(), name='recruiter-stats'),
    path('api/v1/candidate/stats/', CandidateStatsView.as_view(), name='candidate-stats'),
    path('api/v1/stats/cv-registration-rate/', CVRegistrationRateView.as_view(), name='cv_registration_rate'),
    path('api/v1/stats/application-rate/', ApplicationRateView.as_view(), name='application_rate'),
    path('api/v1/job-postings/', home_views.JobPostingsView.as_view(), name='job-postings'),
    path('api/v1/job-postings/latest/', home_views.JobPostingsView.as_view(), name='latest-job-postings'),
    path('api/v1/job-postings/<int:pk>/', home_views.JobPostingsView.as_view(), name='job-posting'),
    path('api/v1/locations/', home_views.LocationsView.as_view(), name='locations'),
    path('api/v1/categories/', home_views.CategoriesView.as_view(), name='categories'),
    path('', include(router.urls)),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
