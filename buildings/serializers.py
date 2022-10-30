from .models import Buildings,Buildingaccess
from rest_framework import serializers 
from datetime import datetime

class BuildingRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Buildingaccess
        fields = '__all__'
