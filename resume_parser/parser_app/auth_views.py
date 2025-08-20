from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import AllowAny
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from .models import Resume
from django.core.mail import send_mail
from django.utils.crypto import get_random_string

User = get_user_model()


class CandidateRegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        name = request.data.get('name')
        password = request.data.get('password')
        password_confirmation = request.data.get('password_confirmation')

        if password != password_confirmation:
            return Response({'error': 'Passwords do not match'}, status=status.HTTP_400_BAD_REQUEST)

        if not email or not name or not password:
            return Response({'error': 'Please provide email, name, and password'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            validate_password(password)
        except ValidationError as e:
            return Response({'error': e.messages}, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(email=email).exists():
            return Response({'error': 'Email already exists'}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.create_user(email=email, name=name, password=password, role=User.CANDIDATE)

        refresh = RefreshToken.for_user(user)
        return Response({
            'refresh': str(refresh),
            'token': str(refresh.access_token),
            'name': user.name,
            'role': user.role,
        }, status=status.HTTP_201_CREATED)


class RecruiterRegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        name = request.data.get('name')
        password = request.data.get('password')
        password_confirmation = request.data.get('password_confirmation')
        company = request.data.get('company')
        position = request.data.get('position')

        if password != password_confirmation:
            return Response({'error': 'Passwords do not match'}, status=status.HTTP_400_BAD_REQUEST)

        if not email or not name or not password or not company:
            return Response({'error': 'Please provide email, name, password, and company'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            validate_password(password)
        except ValidationError as e:
            return Response({'error': e.messages}, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(email=email).exists():
            return Response({'error': 'Email already exists'}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.create_user(email=email, name=name, password=password, role=User.RECRUITER, company=company, position=position)

        refresh = RefreshToken.for_user(user)
        return Response({
            'refresh': str(refresh),
            'token': str(refresh.access_token),
            'name': user.name,
            'role': user.role,
        }, status=status.HTTP_201_CREATED)


# class RegisterView(APIView):
#     permission_classes = [AllowAny]
#
#     def post(self, request):
#         email = request.data.get('email')
#         name = request.data.get('name')
#         password = request.data.get('password')
#         role = request.data.get('role', User.CANDIDATE)  # Default to CANDIDATE if not specified
#
#         if not email or not name or not password:
#             return Response({'error': 'Please provide email, name, and password'}, status=status.HTTP_400_BAD_REQUEST)
#
#         if role not in [choice[0] for choice in User.ROLE_CHOICES]:
#             return Response({'error': 'Invalid role'}, status=status.HTTP_400_BAD_REQUEST)
#
#         try:
#             validate_password(password)
#         except ValidationError as e:
#             return Response({'error': e.messages}, status=status.HTTP_400_BAD_REQUEST)
#
#         if User.objects.filter(email=email).exists():
#             return Response({'error': 'Email already exists'}, status=status.HTTP_400_BAD_REQUEST)
#
#         user = User.objects.create_user(email=email, name=name, password=password, role=role)
#
#         if role == User.CANDIDATE:
#             Resume.objects.create(user=user, email=email, name=name)
#
#         refresh = RefreshToken.for_user(user)
#
#         return Response({
#             'refresh': str(refresh),
#             'token': str(refresh.access_token),
#             'name': user.name,
#             'role': user.role,
#         }, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        user = User.objects.filter(email=email).first()

        if user is None or not user.check_password(password):
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

        refresh = RefreshToken.for_user(user)

        return Response({
            'refresh': str(refresh),
            'token': str(refresh.access_token),
            'name': user.name,
            'role': user.role,
        })


class RequestPasswordResetView(APIView):
    def post(self, request):
        email = request.data.get('email')
        if not email:
            return Response({'error': 'Email is required'}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.filter(email=email).first()
        if user:
            # Generate a token
            token = get_random_string(length=32)

            # Save the token (you might want to create a separate model for this)
            user.password_reset_token = token
            user.save()

            # Send email
            reset_url = f"http://cvjob.online/password/reset?token={token}"
            send_mail(
                'Password Reset',
                f'Click here to reset your password: {reset_url}',
                'contact@housnijob.com',
                [email],
                fail_silently=False,
            )

            return Response({'message': 'Password reset email sent'}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)


class ResetPasswordView(APIView):
    def post(self, request):
        token = request.data.get('token')
        new_password = request.data.get('new_password')
        new_password_confirmation = request.data.get('new_password_confirmation')

        if not token or not new_password:
            return Response({'error': 'Token and new password are required'}, status=status.HTTP_400_BAD_REQUEST)

        if new_password != new_password_confirmation:
            return Response({'error': 'Passwords do not match'}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.filter(password_reset_token=token).first()
        if user:
            user.set_password(new_password)
            user.password_reset_token = None  # Clear the token
            user.save()

            # Generate new JWT tokens
            refresh = RefreshToken.for_user(user)

            return Response({
                'message': 'Password reset successful',
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Invalid or expired token'}, status=status.HTTP_400_BAD_REQUEST)
