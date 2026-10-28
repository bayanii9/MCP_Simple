from django.urls import path
from .views import HomeworkAPIView

urlpatterns = [
    path("homework/", HomeworkAPIView.as_view()),
]