from django.apps import apps
from django.test import TestCase

from .models import Category, Task


class TaskSchemaTests(TestCase):
    def test_registered_task_can_be_created_and_retrieved(self):
        task_model = apps.get_model("catalog", "Task")
        self.assertIs(task_model, Task)
        category = Category.objects.create(name="Writing", slug="writing")
        task = task_model.objects.create(
            slug="summarize", title="Summarize", short_description="Summarize text",
            category=category,
        )
        saved = task_model.objects.get(pk=task.pk)
        self.assertEqual(saved.category, category)
        self.assertEqual(saved.status, Task.Status.DRAFT)
        self.assertEqual(saved.credit_cost, 0)
        self.assertEqual(task_model.objects.count(), 1)
