from django.urls import path

from .views import (
    GenerateTemporaryIdsView,
    UploadTemporaryIdsView,
    GetInfectionStatusView,
    GetUploadRequirementStatusView,
    UserRetrieveUpdateAPIView
)

app_name = 'contacts'

urlpatterns = [
    path('temp_id', GenerateTemporaryIdsView.as_view()),
    path('upload', UploadTemporaryIdsView.as_view()),
    path('upload/status', GetUploadRequirementStatusView.as_view()),
    path('status', GetInfectionStatusView.as_view()),
    path('user', UserRetrieveUpdateAPIView.as_view()),
]