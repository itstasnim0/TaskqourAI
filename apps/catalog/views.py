from rest_framework import generics

from .models import Task
from .serializers import TaskDetailSerializer, TaskListSerializer


class TaskListView(generics.ListAPIView):
    queryset = Task.objects.filter(
        status=Task.Status.ACTIVE
    ).select_related("category")
    serializer_class = TaskListSerializer


class TaskDetailView(generics.RetrieveAPIView):
    queryset = Task.objects.filter(
        status=Task.Status.ACTIVE
    ).prefetch_related(
        "form_fields",
        "definitions",
    )
    serializer_class = TaskDetailSerializer
    lookup_field = "slug"
