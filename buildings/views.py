from django.shortcuts import render
from django.utils import timezone
from .models import Buildings, Buildingaccess, Users
from rest_framework.exceptions import ValidationError
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from datetime import date, datetime, timedelta
from .serializers import BuildingRegisterSerializer


import logging
logger = logging.getLogger('loki')

# Create your views here.
class BuildingAccessRegister (CreateAPIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        try:
            user = Users.objects.get(id=request.user.id)
        except Users.DoesNotExist:
            raise ValidationError(detail="User does not exist")
            
        logger.info('User accessed building.', extra={'action': 'building_access', 'request': request, 'user_id': request.user.id})
        try:
            building = Buildings.objects.get(id=request.data['building'])
        except:
            logger.warn('Building does not exist.', extra={'action': 'building_access', 'request': request, 'user_id': user.id})
            raise ValidationError(detail="Building does not exist")
            
        infection = user.infectionhistory_set.filter( 
            recorded_timestamp__range=(datetime.combine(date.today(), datetime.min.time(), timezone.now().tzinfo)-timedelta(days=15), timezone.now().replace(hour=23, minute=59, second=59, microsecond=999999))
            )
        if infection.exists():
            return Response(data={'building_name': building.name, 'infected':True}, status=status.HTTP_200_OK)

        request.data['user'] = request.user.id
        request.data['access_timestamp'] = timezone.now()
        buildingaccess = BuildingRegisterSerializer(data=request.data)
        buildingaccess.is_valid(raise_exception=True)
        buildingaccess.save()

        return Response(data={'building_name': building.name, 'infected': False}, status=status.HTTP_201_CREATED)
