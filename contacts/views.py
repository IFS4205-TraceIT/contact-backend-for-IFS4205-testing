from django.conf import settings
from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView, CreateAPIView, RetrieveUpdateAPIView
from rest_framework.response import Response
from datetime import date, timedelta, datetime
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny, IsAuthenticated

from accounts.vault import create_vault_client
from .models import (
    Infectionhistory,
    Closecontacts,
    Notifications
)
from .serializers import (
    CloseContactSerializer,
    UserSerializer
)
from .utils import get_or_generate_secret_key, generate_temp_ids, decrypt_temp_id

import logging
logger = logging.getLogger('loki')

# Create your views here.
class GenerateTemporaryIdsView(ListAPIView):

    permission_classes = (IsAuthenticated,)

    def list(self, request):
        user_id = request.user.id
        vault_client = create_vault_client()
        temp_id_key = get_or_generate_secret_key(vault_client, settings.VAULT_TEMP_ID_KEY_PATH)
        temp_ids, start_time = generate_temp_ids(user_id, temp_id_key)
        payload = {
            'temp_ids': temp_ids,
            'server_start_time': start_time,
        }
        logging.info('Generated temporary IDs.', extra={'action': 'generate_temp_ids', 'request': request, 'user_id': user_id})
        return Response(data=payload, status=status.HTTP_200_OK)


class UploadTemporaryIdsView(CreateAPIView):

    permission_classes = (IsAuthenticated,)
    serializer_class = CloseContactSerializer

    def create(self, request):
        user_id = request.user.id
        logging.info('Upload temporary IDs.', extra={'action': 'upload_temp_ids', 'request': request, 'user_id': user_id})
        user_recent_infection_history = Infectionhistory.objects.filter(
            user_id = user_id,
            recorded_timestamp__range=(
                timezone.now() - timedelta(days=15),
                timezone.now()
            ))
        if user_recent_infection_history.count() == 0:
            raise ValidationError('User has no recent infection history')
        
        user_recent_infection = user_recent_infection_history.latest("recorded_timestamp")
        
        notification = Notifications.objects.filter(infection_id=user_recent_infection.id, uploaded_status=False)
        if not notification.exists():
            raise ValidationError('User has no recent infection history')
        latest_notification = notification.latest('due_date')

        if latest_notification.due_date < timezone.now().date():
            raise ValidationError('User has no recent infection history')

        temp_ids = request.data.get('temp_ids')
        if temp_ids is None or type(temp_ids) != list or len(temp_ids) == 0:
            raise ValidationError('Missing temp_ids')
        
        vault_client = create_vault_client()
        temp_id_key = get_or_generate_secret_key(vault_client, settings.VAULT_TEMP_ID_KEY_PATH)
        final_temp_ids = list(filter(lambda x: decrypt_temp_id(x, temp_id_key, user_id, user_recent_infection.id), temp_ids))
        
        if len(final_temp_ids) == 0:
            raise ValidationError('No valid temp_ids')
        
        serial = self.serializer_class(data=final_temp_ids, many=True)
        serial.is_valid(raise_exception=True)

        latest_notification.uploaded_status = True
        serial.save()
        latest_notification.save()
        logging.info('Uploaded temporary IDs.', extra={'action': 'upload_temp_ids', 'request': request, 'user_id': user_id})
        return Response(status=status.HTTP_201_CREATED)


class GetInfectionStatusView(APIView):

    permission_classes = (IsAuthenticated,)

    def get(self, request):
        user_id = request.user.id
        logging.info('Get infection status.', extra={'action': 'get_infection_status', 'request': request, 'user_id': user_id})
        user_recent_infection_history = Infectionhistory.objects.filter(
            user_id = user_id,
            recorded_timestamp__range=(
                timezone.now() - timedelta(days=15),
                timezone.now()
            ))
        if user_recent_infection_history.count() > 0:
            return Response(data={'status': 'positive'}, status=status.HTTP_200_OK)

        user_recent_close_contact_history = Closecontacts.objects.filter(
            contacted_user_id = user_id,
            contact_timestamp__range=(
                timezone.now() - timedelta(days=15),
                timezone.now()
            )
        )

        if user_recent_close_contact_history.count() > 0:
            return Response(data={'status': 'close'}, status=status.HTTP_200_OK)

        return Response(data={'status': 'negative'}, status=status.HTTP_200_OK)


class GetUploadRequirementStatusView(APIView):

    permission_classes = (IsAuthenticated,)

    def get(self, request):
        user_id = request.user.id
        logging.info('Get upload requirement status.', extra={'action': 'get_upload_requirement_status', 'request': request, 'user_id': user_id})
        if Notifications.objects.filter(infection__user_id=user_id, start_date__lte=timezone.now().date(), due_date__gte=timezone.now().date(), uploaded_status=False).exists():
            return Response(data={'status': True}, status=status.HTTP_200_OK)
        return Response(data={'status': False}, status=status.HTTP_200_OK)


class UserRetrieveUpdateAPIView(RetrieveUpdateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = UserSerializer

    def retrieve(self, request) -> Response:
        """Return user on GET request."""
        logging.info('Get user details.', extra={'action': 'get_user', 'request': request, 'user_id': request.user.id})
        queryset = UserSerializer.Meta.model.objects.all()
        user = get_object_or_404(queryset, id=request.user.id)
        serializer = self.serializer_class(user, context={'request': request})

        return Response(serializer.data, status=status.HTTP_200_OK) 

    def update(self, request) -> Response:
        """Return updated user."""
        return Response(status=status.HTTP_501_NOT_IMPLEMENTED)
        # serializer_data = request.data
        # logging.info('Update user details.', extra={'action': 'update_user', 'request': request, 'user_id': request.user.id})
        # queryset = UserSerializer.Meta.model.objects.all()
        # user = get_object_or_404(queryset, id=request.user.id)

        # serializer_data['phone'] = request.user.phone_number
        # serializer_data['email'] = request.user.email

        # if 'nric' in serializer_data:
        #     raise ValidationError('nric cannot be updated')

        # serializer = self.serializer_class(
        #     user, data=serializer_data, partial=True, context={'request': request}
        # )
        # serializer.is_valid(raise_exception=True)
        # serializer.save()

        # return Response(serializer.data, status=status.HTTP_200_OK)