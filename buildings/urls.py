from django.urls import path

from .views import (
    BuildingAccessRegister
)

app_name = 'infections'

urlpatterns = [
    path('register', BuildingAccessRegister.as_view()),
]
