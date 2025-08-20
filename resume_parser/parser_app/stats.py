from django.utils import timezone
from datetime import timedelta
from django.db.models import Count
from django.db.models.functions import TruncDate
from .models import Resume, CustomUser, JobPosting, Application
from datetime import datetime


def get_cv_registration_rate(period='week'):
    today = timezone.now().date()

    if period == 'week':
        start_date = today - timedelta(days=6)  # 7 days including today
    elif period == 'month':
        start_date = today - timedelta(days=29)  # 30 days including today
    elif period == 'year':
        start_date = today - timedelta(days=364)  # 365 days including today
    else:
        start_date = today - timedelta(days=6)  # Default to week

    # Generate all dates in the range
    date_range = [start_date + timedelta(days=x) for x in range((today - start_date).days + 1)]

    # Get all resumes for the selected period in a single query
    resumes = Resume.objects.filter(uploaded_on__date__gte=start_date) \
        .annotate(date=TruncDate('uploaded_on')) \
        .values('date') \
        .annotate(count=Count('id')) \
        .order_by('date')

    # Convert queryset to a dictionary for easier lookup
    resume_dict = resume_dict = {r['date'].date() if isinstance(r['date'], datetime) else r['date']: r['count'] for r in resumes}

    # Get total resumes count up to the start date
    total_resumes = Resume.objects.filter(uploaded_on__date__lt=start_date).count()

    daily_rates = []
    cumulative_count = total_resumes

    for current_date in date_range:
        daily_count = resume_dict.get(current_date, 0)
        cumulative_count += daily_count
        rate = (daily_count / cumulative_count) * 100 if cumulative_count > 0 else 0
        daily_rates.append({
            'date': current_date.strftime('%Y-%m-%d'),
            'rate': round(rate, 2)
        })

    return daily_rates


def get_admin_stats():
    user_counts = CustomUser.objects.values('role').annotate(count=Count('id'))
    stats = {
        'recruiters_count': 0,
        'candidates_count': 0,
        'resumes_count': Resume.objects.count(),
        'offers_count': JobPosting.objects.count(),
        'admins_count': 0,
        'applications_count': Application.objects.count()
    }
    for count in user_counts:
        if count['role'] == CustomUser.RECRUITER:
            stats['recruiters_count'] = count['count']
        elif count['role'] == CustomUser.CANDIDATE:
            stats['candidates_count'] = count['count']
        elif count['role'] == CustomUser.ADMIN:
            stats['admins_count'] = count['count']
    return stats


def get_recruiter_stats(user):
    stats = {
        'offers_count': JobPosting.objects.filter(recruiter=user).count(),
        'applications_count': Application.objects.filter(job__recruiter=user).count(),
        'open_offers_count': JobPosting.objects.filter(recruiter=user, status=True).count(),
        'closed_offers_count': JobPosting.objects.filter(recruiter=user, status=False).count(),
    }

    popular_jobs = Application.objects.filter(job__recruiter=user).values('job__title').annotate(count=Count('id')).order_by('-count')

    if popular_jobs:
        stats['most_popular_job_title'] = popular_jobs.first()['job__title']
        stats['least_popular_job_title'] = popular_jobs.last()['job__title']
    else:
        stats['most_popular_job_title'] = "Aucun candidat n'a postulé pour le moment"
        stats['least_popular_job_title'] = "Aucun candidat n'a postulé pour le moment"

    return stats


def get_candidate_stats(user):
    stats = {
        'applications_count': Application.objects.filter(candidate=user).count(),
        'accepted_applications_count': Application.objects.filter(candidate=user, status=Application.ACCEPTED).count(),
        'rejected_applications_count': Application.objects.filter(candidate=user, status=Application.REJECTED).count(),
        'pending_applications_count': Application.objects.filter(candidate=user, status=Application.PENDING).count(),
    }

    most_applied_category = Application.objects.filter(candidate=user).values('job__category').annotate(count=Count('id')).order_by('-count').first()
    if most_applied_category:
        stats['most_applied_job_category'] = most_applied_category['job__category']
    else:
        stats['most_applied_job_category'] = "Aucune candidature n'a été soumise pour le moment"

    most_applied_city = Application.objects.filter(candidate=user).values('job__city').annotate(count=Count('id')).order_by('-count').first()
    if most_applied_city:
        stats['most_applied_job_city'] = most_applied_city['job__city']
    else:
        stats['most_applied_job_city'] = "Aucune candidature n'a été soumise pour le moment"

    return stats


def get_application_rate(period='week'):
    today = timezone.now().date()

    if period == 'week':
        start_date = today - timedelta(days=6)  # 7 days including today
    elif period == 'month':
        start_date = today - timedelta(days=29)  # 30 days including today
    elif period == 'year':
        start_date = today - timedelta(days=364)  # 365 days including today
    else:
        start_date = today - timedelta(days=6)  # Default to week

    # Generate all dates in the range
    date_range = [start_date + timedelta(days=x) for x in range((today - start_date).days + 1)]

    # Get all resumes for the selected period in a single query
    applications = Application.objects.filter(applied_on__date__gte=start_date) \
        .annotate(date=TruncDate('applied_on')) \
        .values('date') \
        .annotate(count=Count('id')) \
        .order_by('date')

    # Convert queryset to a dictionary for easier lookup
    application_dict = application_dict = {a['date'].date() if isinstance(a['date'], datetime) else a['date']: a['count'] for a in applications}

    # Get total resumes count up to the start date
    total_applications = Application.objects.filter(applied_on__date__lt=start_date).count()

    daily_rates = []
    cumulative_count = total_applications

    for current_date in date_range:
        daily_count = application_dict.get(current_date, 0)
        cumulative_count += daily_count
        rate = (daily_count / cumulative_count) * 100 if cumulative_count > 0 else 0
        daily_rates.append({
            'date': current_date.strftime('%Y-%m-%d'),
            'rate': round(rate, 2)
        })

    return daily_rates