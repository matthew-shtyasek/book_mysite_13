from django.contrib import admin
from parler.admin import TranslatableAdmin

from courses.models import Subject, Course, Module


@admin.register(Subject)
class SubjectAdmin(TranslatableAdmin):
    list_display = ['title', 'slug']

    def get_prepopulated_fields(self, request, obj=None):
        return {'slug': ('title', )}


class ModuleInline(admin.StackedInline):
    model = Module


@admin.register(Course)
class CourseAdmin(TranslatableAdmin):
    list_display = ['title', 'slug', 'subject', 'created']
    list_filter = ['created', 'subject']
    search_fields = ['translations__title', 'translations__slug', 'overview']
    inlines = [ModuleInline]

    def get_prepopulated_fields(self, request, obj=None):
        return {'slug': ('title', )}
