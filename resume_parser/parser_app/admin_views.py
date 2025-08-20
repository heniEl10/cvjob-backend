from django.contrib.contenttypes.models import ContentType
from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from .models import CustomUser, Resume, JobPosting, Application
from .serializers import CandidateSerializer, ResumeSerializer, JobPostingSerializer, ApplicationSerializer, RecruiterSerializer
from django.http import FileResponse
from django.conf import settings
import os
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from django.db import transaction
from .permissions import IsAdmin, IsRecruiter, IsCandidate, IsAdminOrRecruiter


class CustomPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

    def get_paginated_response(self, data):
        return Response({
            'links': {
                'next': self.get_next_link(),
                'previous': self.get_previous_link()
            },
            'count': self.page.paginator.count,
            'total_pages': self.page.paginator.num_pages,
            'results': data
        })


class AdminCandidateViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.filter(role=CustomUser.CANDIDATE)
    serializer_class = CandidateSerializer
    permission_classes = [IsAdmin]
    pagination_class = CustomPagination
    search_fields = ['name', 'email']

    def perform_create(self, serializer):
        serializer.save(role=CustomUser.CANDIDATE)

    def get_queryset(self):
        queryset = CustomUser.objects.filter(role=CustomUser.CANDIDATE)
        search_term = self.request.query_params.get('search', None)

        if search_term:
            queryset = queryset.filter(
                Q(name__icontains=search_term) |
                Q(email__icontains=search_term)
            )

        return queryset.distinct()

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        with transaction.atomic():
            Resume.objects.filter(user=instance).delete()

            instance.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)


class AdminRecruiterViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.filter(role=CustomUser.RECRUITER)
    serializer_class = RecruiterSerializer
    permission_classes = [IsAdmin]
    pagination_class = CustomPagination
    search_fields = ['name', 'email', 'company', 'position']

    def perform_create(self, serializer):
        serializer.save(role=CustomUser.RECRUITER)

    def get_queryset(self):
        queryset = CustomUser.objects.filter(role=CustomUser.RECRUITER)
        search_term = self.request.query_params.get('search', None)

        if search_term:
            queryset = queryset.filter(
                Q(name__icontains=search_term) |
                Q(email__icontains=search_term) |
                Q(company__icontains=search_term) |
                Q(position__icontains=search_term)
            )

        return queryset.distinct()

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        with transaction.atomic():
            JobPosting.objects.filter(recruiter=instance).delete()

            instance.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)


EDUCATION_LEVELS = {
    '1': ['Bac', 'Baccalauréat', 'BAC', 'niveau bac'],
    '2': ['DEUG', 'DUT', 'BTS', 'BAC+2', 'DEUST'],
    '3': ['Licence', 'BAC+3', 'Bachelor', 'LST', 'Licencié'],
    '4': ['BAC+4', 'M1'],
    '5': ['Master', 'BAC+5', 'M2', 'Diplôme d\'ingénieur', 'Ingénieur', 'Ingénieur d\'état', 'Ingénierie'],
    '8': ['Doctorat', 'PhD']
}


class AdminResumeViewSet(viewsets.ModelViewSet):
    queryset = Resume.objects.all()
    serializer_class = ResumeSerializer
    pagination_class = CustomPagination
    permission_classes = [IsAdmin]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['name', 'email', 'skills', 'education', 'experience']

    def get_queryset(self):
        queryset = Resume.objects.all()
        search_term = self.request.query_params.get('search', None)
        education_filter = self.request.query_params.get('education', None)

        if search_term:
            queryset = queryset.filter(
                Q(name__icontains=search_term) |
                Q(email__icontains=search_term) |
                Q(skills__icontains=search_term) |
                Q(education__icontains=search_term) |
                Q(experience__icontains=search_term)
            )

        if education_filter and education_filter.lower() != 'all':
            education_terms = EDUCATION_LEVELS.get(education_filter, [])
            if education_terms:
                education_query = Q()
                for term in education_terms:
                    education_query |= Q(education__icontains=term)
                queryset = queryset.filter(education_query)

        return queryset.distinct()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['get'], permission_classes=[IsAdminOrRecruiter])
    def download(self, request, pk=None):
        resume = self.get_object()
        if resume.resume:
            file_path = os.path.join(settings.MEDIA_ROOT, str(resume.resume))
            if os.path.exists(file_path):
                response = FileResponse(open(file_path, 'rb'), content_type='application/pdf')
                response['Content-Disposition'] = f'attachment; filename="{os.path.basename(file_path)}"'
                return response
        return Response({"detail": "Resume file not found"}, status=status.HTTP_404_NOT_FOUND)


class AdminJobPostingViewSet(viewsets.ModelViewSet):
    queryset = JobPosting.objects.all()
    serializer_class = JobPostingSerializer
    permission_classes = [IsAdmin, IsRecruiter]
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['title', 'description', 'city', 'category']

    def perform_create(self, serializer):
        company_logo = self.request.data.get('company_logo')
        serializer.save(recruiter=self.request.user, company_logo=company_logo)

    def perform_update(self, serializer):
        instance = serializer.instance
        company_logo = self.request.data.get('company_logo')

        if company_logo:
            # Delete old company logo if it exists
            if instance.company_logo:
                instance.company_logo.delete()

            # Save new company logo
            instance.company_logo = company_logo

        serializer.save()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    def get_queryset(self):
        queryset = JobPosting.objects.all()
        search_term = self.request.query_params.get('search', None)
        location_filter = self.request.query_params.get('location', None)
        category_filter = self.request.query_params.get('category', None)

        if search_term:
            queryset = queryset.filter(
                Q(title__icontains=search_term) |
                Q(description__icontains=search_term) |
                Q(city__icontains=search_term) |
                Q(category__icontains=search_term)
            )

        if location_filter and location_filter.lower() != 'all':
            queryset = queryset.filter(city__iexact=location_filter)

        if category_filter and category_filter.lower() != 'all':
            queryset = queryset.filter(category__iexact=category_filter)

        return queryset.distinct()

    @action(detail=True, methods=['get'])
    def applicants(self, request, pk=None):
        job_posting = self.get_object()
        applications = job_posting.applications.all()
        serializer = ApplicationSerializer(applications, many=True)
        return Response(serializer.data)


class RecruiterJobPostingViewSet(viewsets.ModelViewSet):
    serializer_class = JobPostingSerializer
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['title', 'description', 'city', 'category']
    permission_classes = [IsAdminOrRecruiter]

    def get_queryset(self):
        queryset = JobPosting.objects.filter(recruiter=self.request.user)
        search_term = self.request.query_params.get('search', None)
        location_filter = self.request.query_params.get('location', None)
        category_filter = self.request.query_params.get('category', None)

        if search_term:
            queryset = queryset.filter(
                Q(title__icontains=search_term) |
                Q(description__icontains=search_term) |
                Q(city__icontains=search_term) |
                Q(category__icontains=search_term)
            )

        if location_filter and location_filter.lower() != 'all':
            queryset = queryset.filter(city__iexact=location_filter)

        if category_filter and category_filter.lower() != 'all':
            queryset = queryset.filter(category__iexact=category_filter)

        return queryset.distinct()

    def perform_create(self, serializer):
        company_logo = self.request.data.get('company_logo')
        serializer.save(recruiter=self.request.user, company_logo=company_logo)

    def perform_update(self, serializer):
        instance = serializer.instance
        company_logo = self.request.data.get('company_logo')

        if company_logo:
            # Delete old company logo if it exists
            if instance.company_logo:
                instance.company_logo.delete()

            # Save new company logo
            instance.company_logo = company_logo

        serializer.save()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()

        if instance.recruiter != request.user:
            return Response({"detail": "You do not have permission to update this job posting."},
                            status=status.HTTP_403_FORBIDDEN)

        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def applicants(self, request, pk=None):
        job_posting = self.get_object()

        if job_posting.recruiter != request.user:
            return Response({"detail": "You do not have permission to view applicants for this job posting."},
                            status=status.HTTP_403_FORBIDDEN)

        applications = job_posting.applications.all()
        serializer = ApplicationSerializer(applications, many=True)
        return Response(serializer.data)

