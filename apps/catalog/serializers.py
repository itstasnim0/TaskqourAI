from rest_framework import serializers

from .models import FormField, Task, TaskDefinition


class FormFieldSerializer(serializers.ModelSerializer):
    class Meta:
        model = FormField
        fields = (
            "id",
            "key",
            "label",
            "help_text",
            "field_type",
            "options",
            "is_required",
            "order",
            "validation",
            "placeholder",
        )


class TaskDefinitionSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskDefinition
        fields = (
            "id",
            "version",
            "role",
            "process",
            "rules",
            "constraints",
            "output_structure",
            "output_template",
            "examples",
            "is_active",
        )


class TaskListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = (
            "id",
            "slug",
            "title",
            "short_description",
            "icon",
            "status",
            "estimated_seconds",
            "credit_cost",
            "sample_output",
        )


class TaskDetailSerializer(serializers.ModelSerializer):
    form_fields = FormFieldSerializer(many=True, read_only=True)
    definitions = TaskDefinitionSerializer(many=True, read_only=True)

    class Meta:
        model = Task
        fields = (
            "id",
            "slug",
            "title",
            "short_description",
            "icon",
            "status",
            "estimated_seconds",
            "credit_cost",
            "sample_output",
            "form_fields",
            "definitions",
        )
