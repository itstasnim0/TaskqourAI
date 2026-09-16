import uuid

from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name


class Task(models.Model):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        ACTIVE = "active", "Active"
        DISABLED = "disabled", "Disabled"

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    slug = models.SlugField(unique=True)
    title = models.TextField()
    short_description = models.TextField()

    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="tasks",
    )

    icon = models.CharField(max_length=255, blank=True)

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT,
    )

    estimated_seconds = models.IntegerField(default=0)
    credit_cost = models.IntegerField(default=0)
    sample_output = models.TextField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
    

class TaskDefinition(models.Model):
    class OutputStructure(models.TextChoices):
        FREE_TEXT = "free_text", "Free text"
        MARKDOWN = "markdown", "Markdown"
        JSON = "json", "JSON"
        TEMPLATE = "template", "Template"

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name="definitions",
    )

    version = models.IntegerField()

    role = models.TextField()
    process = models.JSONField(default=list)
    rules = models.JSONField(default=list)
    constraints = models.JSONField(default=list)

    output_structure = models.CharField(
        max_length=20,
        choices=OutputStructure.choices,
    )

    output_template = models.TextField(
        null=True,
        blank=True,
    )

    examples = models.JSONField(
        null=True,
        blank=True,
    )

    is_active = models.BooleanField(default=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["task", "version"],
                name="unique_task_definition_version",
            ),
        ]

    def __str__(self):
        return f"{self.task.title} - v{self.version}"


class FormField(models.Model):
    class FieldType(models.TextChoices):
        SHORT_TEXT = "short_text", "Short text"
        LONG_TEXT = "long_text", "Long text"
        SELECT = "select", "Select"
        MULTI_SELECT = "multi_select", "Multi select"
        NUMBER = "number", "Number"
        BOOLEAN = "boolean", "Boolean"

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name="form_fields",
    )

    key = models.CharField(max_length=100)
    label = models.TextField()
    help_text = models.TextField(blank=True)

    field_type = models.CharField(
        max_length=20,
        choices=FieldType.choices,
    )

    options = models.JSONField(
        null=True,
        blank=True,
    )

    is_required = models.BooleanField(default=False)
    order = models.IntegerField(default=0)

    validation = models.JSONField(default=dict)

    placeholder = models.CharField(
        max_length=255,
        blank=True,
    )

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return self.label
