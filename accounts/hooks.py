# Every backend has a special requirement after registraion and login.
# The hook is a way to add this requirement to the backend.

from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from .models import AuthUser
from .serializers import UserSerializer
from contacts.models import Users
from contacts.serializers import UserSerializer as ContactUserSerializer

import logging
logger = logging.getLogger('loki')

def post_registration_hook(request: Request, serializer: UserSerializer):
    """
    This function is called after a user registers.
    """
    user_request = request.data
    user = Users(id=serializer.data['id'])
    contact_serializer = ContactUserSerializer(user, data=user_request, context={'request': request})
    user_request['phone'] = serializer.data['phone_number']
    if not contact_serializer.is_valid():
        AuthUser.objects.get(id=serializer.data['id']).delete()
        return Response(contact_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    contact_serializer.save()
    logger.info('User registered.', extra={'action': 'register', 'request': request, 'user_id': serializer.data['id']})
    del serializer.data['id']
    returned_data = {**serializer.data, **contact_serializer.data}
    return Response(returned_data, status=status.HTTP_201_CREATED)

def post_login_hook(request: Request, serializer: UserSerializer):
    """
    This function is called after a user logs in.
    """
    try:
        Users.objects.get(id=serializer.data['id'])
    except Users.DoesNotExist:
        logger.warn('User does not have permission to access this portal.', extra={'action': 'login', 'request': request, 'user_id': serializer.data['id']})
        return Response(data={'error':['A user with this username and password was not found.']}, status=status.HTTP_400_BAD_REQUEST)
    logger.info('User logged in.', extra={'action': 'login', 'request': request, 'user_id': serializer.data['id']})
    del serializer.data['id']
    return Response(serializer.data, status=status.HTTP_200_OK)


def check_user(user: AuthUser):
    """
    This function is called after a user logs in.
    """
    try:
        Users.objects.get(id=user.id)
    except Users.DoesNotExist:
        return False
    return True