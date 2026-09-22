from django.urls import path
from apps.executions.views import TaskRunListCreateView, TaskRunDetailView

app_name = "executions"

urlpatterns = [
    path("runs/", TaskRunListCreateView.as_view(), name="run-list-create"),
    path("runs/<uuid:id>/", TaskRunDetailView.as_view(), name="run-detail"),
]
