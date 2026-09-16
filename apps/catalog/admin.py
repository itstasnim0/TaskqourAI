from django.contrib import admin

from .models import Category, FormField, Task, TaskDefinition



@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")


class TaskDefinitionInline(admin.StackedInline):
    model = TaskDefinition
    extra = 0


class FormFieldInline(admin.TabularInline):
    model = FormField
    extra = 0



@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "slug",
        "category",
        "status",
        "estimated_seconds",
        "credit_cost",
        "created_at",
    )

    list_filter = (
        "status",
        "category",
    )

    search_fields = (
        "title",
        "slug",
        "short_description",
    )

    readonly_fields = (
        "id",
        "created_at",
        "updated_at",
    )

    prepopulated_fields = {
        "slug": ("title",),
    }

    inlines = (
        TaskDefinitionInline,
        FormFieldInline,
    )

