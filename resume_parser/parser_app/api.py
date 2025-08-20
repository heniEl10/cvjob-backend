from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import status
from .models import Resume
from .serializers import ResumeSerializer
from resume_parser.resume_parser import ResumeParser
from django.conf import settings
import os
from .stats import get_cv_registration_rate, get_admin_stats, get_recruiter_stats, get_candidate_stats, get_application_rate
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from .permissions import IsAdmin, IsRecruiter, IsCandidate, IsAdminOrRecruiter


class ResumeUploadView(APIView):
    permission_classes = [IsAdmin]
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        files = request.FILES.getlist('resume')

        if not files:
            return Response({"detail": "No files provided"}, status=status.HTTP_400_BAD_REQUEST)

        resumes_data = []
        for file in files:
            resume = Resume(resume=file)
            resume.save()

            parser = ResumeParser(os.path.join(settings.MEDIA_ROOT, resume.resume.name))
            data = parser.get_extracted_data()
            resumes_data.append(data)

            resume.name = data.get('name')
            resume.email = data.get('email')
            resume.mobile_number = data.get('mobile_number')
            resume.education = ', '.join(data.get('education')) if data.get('education') else None
            resume.skills = ', '.join(data.get('skills')) if data.get('skills') else None
            resume.experience = ', '.join(data.get('experience')) if data.get('experience') else None
            resume.save()

        serializer = ResumeSerializer(Resume.objects.all(), many=True)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class CVRegistrationRateView(APIView):
    permission_classes = [IsAdmin]

    # @method_decorator(cache_page(60 * 30))
    def get(self, request):
        period = request.GET.get('period', 'week')
        data = get_cv_registration_rate(period)
        return Response(data)


class ApplicationRateView(APIView):
    permission_classes = [IsCandidate]

    def get(self, request):
        period = request.GET.get('period', 'week')
        data = get_application_rate(period)
        return Response(data)


class AdminStatsView(APIView):
    permission_classes = [IsAdmin]

    # @method_decorator(cache_page(60 * 30))
    def get(self, request):
        data = get_admin_stats()
        return Response(data)


class RecruiterStatsView(APIView):
    permission_classes = [IsRecruiter]

    # @method_decorator(cache_page(60 * 30))
    def get(self, request):
        data = get_recruiter_stats(request.user)
        return Response(data)


class CandidateStatsView(APIView):
    permission_classes = [IsCandidate]

    # @method_decorator(cache_page(60 * 30))
    def get(self, request):
        data = get_candidate_stats(request.user)
        return Response(data)
