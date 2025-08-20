from django.contrib.auth import get_user_model
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext as _
from .models import Resume, JobPosting, Application
from .serializers import ResumeSerializer, JobPostingSerializer, ApplicationSerializer
from .permissions import IsCandidate
from django.http import FileResponse
import os
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from resume_parser.resume_parser import ResumeParser


class CandidateViewSet(viewsets.ModelViewSet):
    permission_classes = [IsCandidate]
    parser_classes = [JSONParser, MultiPartParser, FormParser]

    def get_queryset(self):
        if self.action in ['retrieve', 'update', 'partial_update', 'destroy', 'download']:
            return Resume.objects.filter(user=self.request.user)
        elif self.action == 'list_jobs':
            return JobPosting.objects.filter(status=True)
        elif self.action in ['apply', 'list_applications']:
            return Application.objects.filter(candidate=self.request.user)

    def get_serializer_class(self):
        if self.action in ['retrieve', 'update', 'partial_update', 'list', 'create', 'upload_resume', 'my_resume']:
            return ResumeSerializer
        elif self.action == 'list_jobs':
            return JobPostingSerializer
        elif self.action in ['apply', 'list_applications']:
            return ApplicationSerializer
        return None

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['get', 'put', 'patch'])
    def my_resume(self, request):
        try:
            resume = Resume.objects.get(user=request.user)
        except Resume.DoesNotExist:
            if request.method == 'GET':
                return Response({"detail": _("Vous n'avez pas encore de CV.")}, status=status.HTTP_404_NOT_FOUND)
            resume = Resume(user=request.user)

        if request.method == 'GET':
            serializer = self.get_serializer(resume)
            return Response(serializer.data)

        elif request.method in ['PUT', 'PATCH']:
            serializer = self.get_serializer(resume, data=request.data, partial=(request.method == 'PATCH'))
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def upload_resume(self, request):
        if 'resume' not in request.FILES:
            return Response({"detail": _("Aucun fichier n'a été fourni.")}, status=status.HTTP_400_BAD_REQUEST)

        file = request.FILES['resume']

        try:
            resume = Resume.objects.get(user=request.user)
            # Delete old file if it exists
            if resume.resume:
                if os.path.isfile(resume.resume.path):
                    os.remove(resume.resume.path)
        except ObjectDoesNotExist:
            resume = Resume(user=request.user)

        resume.resume = file
        resume.save()

        User = get_user_model()
        user = User.objects.get(pk=request.user.pk)
        name = user.name

        # Parse the resume
        parser = ResumeParser(os.path.join(settings.MEDIA_ROOT, resume.resume.name))
        data = parser.get_extracted_data()

        # Update resume fields
        resume.name = name
        resume.email = data.get('email')
        resume.mobile_number = data.get('mobile_number')
        resume.education = ', '.join(data.get('education')) if data.get('education') else None
        resume.skills = ', '.join(data.get('skills')) if data.get('skills') else None
        resume.experience = ', '.join(data.get('experience')) if data.get('experience') else None
        resume.save()

        serializer = self.get_serializer(resume)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['get'])
    def download(self, request):
        resume = get_object_or_404(Resume, user=request.user)
        if resume.resume:
            file_path = os.path.join(settings.MEDIA_ROOT, str(resume.resume))
            if os.path.exists(file_path):
                response = FileResponse(open(file_path, 'rb'), content_type='application/pdf')
                response['Content-Disposition'] = f'attachment; filename="{os.path.basename(file_path)}"'
                return response
        return Response({"detail": "Resume file not found"}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['get'])
    def list_jobs(self, request):
        jobs = self.get_queryset()
        serializer = self.get_serializer(jobs, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def apply(self, request, pk=None):
        # Try to get the job posting
        try:
            job = JobPosting.objects.get(pk=pk)
        except ObjectDoesNotExist:
            return Response(
                {"detail": _("L'offre d'emploi avec l'identifiant %(pk)s n'a pas été trouvée.") % {'pk': pk}},
                status=status.HTTP_404_NOT_FOUND
            )

        try:
            resume = Resume.objects.get(user=request.user)
        except ObjectDoesNotExist:
            return Response(
                {"detail": _("Aucun CV n'a été trouvé pour votre profil. Veuillez d'abord ajouter un CV.")},
                status=status.HTTP_404_NOT_FOUND
            )

        # Check if the user has already applied
        if Application.objects.filter(job=job, candidate=request.user).exists():
            return Response(
                {"detail": _("Vous avez déjà postulé pour cette offre d'emploi.")},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Create the application
        try:
            application = Application.objects.create(job=job, candidate=request.user, resume=resume)
            serializer = self.get_serializer(application)
            return Response(
                {"detail": _("Votre candidature a été envoyée avec succès."), "data": serializer.data},
                status=status.HTTP_201_CREATED
            )
        except Exception as e:
            return Response(
                {"detail": _("Une erreur est survenue lors de l'envoi de votre candidature. Veuillez réessayer plus tard.")},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['get'])
    def list_applications(self, request):
        applications = self.get_queryset()
        serializer = self.get_serializer(applications, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def check_application(self, request, pk=None):
        job = get_object_or_404(JobPosting, pk=pk)
        has_applied = Application.objects.filter(job=job, candidate=request.user).exists()
        return Response({"has_applied": has_applied}, status=status.HTTP_200_OK)
