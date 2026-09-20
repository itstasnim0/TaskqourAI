import uuid
from django.conf import settings
from django.db import models


class TaskRun(models.Model):
    class Status(models.TextChoices):
        PENDING = "PENDING", "در انتظار اجرا"
        RUNNING = "RUNNING", "در حال اجرا"
        SUCCESS = "SUCCESS", "موفق"
        FAILED = "FAILED", "ناموفق"
        TIMED_OUT = "TIMED_OUT", "پایان مهلت زمانی"

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="task_runs",
        verbose_name="کاربر",
    )

    task = models.ForeignKey(
        "catalog.Task",
        on_delete=models.PROTECT,
        related_name="runs",
        verbose_name="تسک",
    )

    task_definition = models.ForeignKey(
        "catalog.TaskDefinition",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="runs",
        verbose_name="نسخه تعریف تسک",
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True,
        verbose_name="وضعیت",
    )

    input_data = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="داده‌های ورودی کاربر",
    )

    output_data = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="داده‌های خروجی AI",
    )

    error_message = models.TextField(
        blank=True,
        null=True,
        verbose_name="پیام خطا",
    )

    metadata = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="متادیتا و آمار اجرا",
    )

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "اجرای تسک"
        verbose_name_plural = "اجراهای تسک‌ها"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.task.slug} - {self.status} - {self.id}"

