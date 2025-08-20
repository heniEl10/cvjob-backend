from django.http import Http404
from rest_framework.decorators import action
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework.parsers import MultiPartParser, FormParser
from django.db.models import Count
from .models import JobPosting, Blog
from .serializers import JobPostingSerializer, BlogSerializer
from rest_framework.permissions import AllowAny, IsAuthenticatedOrReadOnly
from .permissions import IsAdmin


class JobPostingsView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, pk=None):
        if pk is not None:
            # This is a detail view
            try:
                job_posting = JobPosting.objects.get(pk=pk, status=True)
                serializer = JobPostingSerializer(job_posting)
                return Response(serializer.data)
            except JobPosting.DoesNotExist:
                raise Http404
        else:
            # This is a list view
            queryset = JobPosting.objects.filter(status=True).order_by('-created_on')

            keywords = request.query_params.get('keywords')
            location = request.query_params.get('location')
            category = request.query_params.get('category')

            if keywords:
                queryset = queryset.filter(title__icontains=keywords) | queryset.filter(description__icontains=keywords)
            if location:
                queryset = queryset.filter(city__iexact=location)
            if category:
                queryset = queryset.filter(category__iexact=category)

            serializer = JobPostingSerializer(queryset, many=True)
            return Response(serializer.data)

    # Get the latest 3 job postings: GET /api/v1/job-postings/latest/
    @action(detail=False, methods=['get'])
    def latest(self, request):
        queryset = JobPosting.objects.filter(status=True).order_by('-created_on')[:6]
        serializer = JobPostingSerializer(queryset, many=True)
        return Response(serializer.data)


class LocationsView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        locations = JobPosting.objects.values('city').annotate(count=Count('city')).order_by('-count')
        location_list = [{"id": str(i), "name": location['city']} for i, location in enumerate(locations, 1) if location['city']]
        return Response(location_list)


class CategoriesView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        categories = JobPosting.objects.values('category').annotate(count=Count('category')).order_by('-count')
        category_list = [{"id": str(i), "name": category['category']} for i, category in enumerate(categories, 1) if category['category']]
        return Response(category_list)


class BlogViewSet(viewsets.ModelViewSet):
    queryset = Blog.objects.all()
    serializer_class = BlogSerializer
    lookup_field = 'slug'
    parser_classes = (MultiPartParser, FormParser)

    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'latest']:
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAdmin]
        return [permission() for permission in permission_classes]

    def perform_update(self, serializer):
        instance = serializer.instance
        thumbnail = self.request.data.get('thumbnail')

        if thumbnail:
            # Delete old thumbnail if it exists
            if instance.thumbnail:
                instance.thumbnail.delete()

            # Save new thumbnail
            instance.thumbnail = thumbnail

        serializer.save()

    def perform_create(self, serializer):
        thumbnail = self.request.data.get('thumbnail')
        serializer.save(author=self.request.user, thumbnail=thumbnail)

    # Get the latest 3 blog posts: GET /api/v1/blog/latest/
    @action(detail=False, methods=['get'])
    def latest(self, request):
        queryset = Blog.objects.all().order_by('-created_at')[:3]
        serializer = BlogSerializer(queryset, many=True)
        return Response(serializer.data)
