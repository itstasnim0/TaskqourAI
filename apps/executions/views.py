from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from apps.executions.models import TaskRun
from apps.executions.serializers import (
    TaskRunCreateSerializer,
    TaskRunDetailSerializer,
)


class TaskRunListCreateView(generics.ListCreateAPIView):

    permission_classes = [IsAuthenticated]

    def get_queryset(self):
       
        return (
            TaskRun.objects.filter(user=self.request.user)
            .select_related("task")
            .order_by("-created_at")
        )

    def get_serializer_class(self):
        if self.request.method == "POST":
            return TaskRunCreateSerializer
        return TaskRunDetailSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        task = serializer.validated_data["task"]
     
        active_definition = task.definitions.filter(is_active=True).first()

        task_run = serializer.save(
            user=request.user,
            task_definition=active_definition,
            status=TaskRun.Status.PENDING,
        )

    

        response_serializer = TaskRunDetailSerializer(task_run)
        return Response(response_serializer.data, status=status.HTTP_202_ACCEPTED)


class TaskRunDetailView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = TaskRunDetailSerializer
    lookup_field = "id"

    def get_queryset(self):
        return TaskRun.objects.filter(user=self.request.user).select_related("task")
