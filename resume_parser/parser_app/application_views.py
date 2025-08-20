from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Application
from .serializers import ApplicationSerializer
from .permissions import IsAdminOrRecruiter


class ApplicationViewSet(viewsets.GenericViewSet):
    queryset = Application.objects.all()
    serializer_class = ApplicationSerializer
    permission_classes = [IsAdminOrRecruiter]

    @action(detail=True, methods=['patch'])
    def update_status(self, request, pk=None):
        application = self.get_object()
        new_status = request.data.get('status')

        if not new_status:
            return Response(
                {"error": "status is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if new_status not in dict(Application.STATUS_CHOICES):
            return Response(
                {"error": "Invalid status"},
                status=status.HTTP_400_BAD_REQUEST
            )

        application.status = new_status
        application.save()

        serializer = self.get_serializer(application)
        return Response(serializer.data)

