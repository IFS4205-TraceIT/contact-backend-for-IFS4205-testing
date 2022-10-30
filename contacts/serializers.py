from .models import (
    Users, 
    Closecontacts, 
    Infectionhistory,
    Notifications
    )
from rest_framework import exceptions, serializers 

class CloseContactSerializer(serializers.ModelSerializer):
    """Handle serialization and deserialization of CloseContact objects."""

    class Meta:
        model = Closecontacts
        fields = '__all__'
    

class UserSerializer(serializers.ModelSerializer[Users]):
    """Handle serialization and deserialization of User objects."""

    class Meta:
        model = Users
        fields = (
            'nric',
            'name',
            'dob',
            'email',
            'phone',
            'gender',
            'address',
            'postal_code',
        )
    
    def update(self, instance, validated_data):  # type: ignore
        """Perform an update on a User."""

        for (key, value) in validated_data.items():
            setattr(instance, key, value)

        instance.save()

        return instance