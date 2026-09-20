from rest_framework import serializers
from apps.executions.models import TaskRun


class TaskRunCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = TaskRun
        fields = ["id", "input_data", "status", "created_at"]
        read_only_fields = ["id", "status", "created_at"]

    def validate_input_data(self, value):
        if not isinstance(value, dict):
            raise serializers.ValidationError("ورودی تسک باید یک آبجکت دیکشنری معتبر باشد.")
        return value


class TaskRunDetailSerializer(serializers.ModelSerializer):

    task_slug = serializers.CharField(source="task.slug", read_only=True)
    task_title = serializers.CharField(source="task.title", read_only=True)

    class Meta:
        model = TaskRun
        fields = [
            "id",
            "task_slug",
            "task_title",
            "status",
            "input_data",
            "output_data",
            "error_message",
            "metadata",
            "created_at",
            "started_at",
            "completed_at",
        ]
        read_only_fields = fields
