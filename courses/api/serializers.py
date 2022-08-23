from parler_rest.fields import TranslatedFieldsField
from parler_rest.serializers import TranslatableModelSerializer
from rest_framework.serializers import ModelSerializer

from courses.models import Subject, Course, Module


class SubjectSerializer(TranslatableModelSerializer):
    translations = TranslatedFieldsField(shared_model=Subject)

    class Meta:
        model = Subject
        fields = ['id', 'translations', 'slug']


class ModuleSerializer(ModelSerializer):
    class Meta:
        model = Module
        fields = ['order', 'title', 'description']


class CourseSerializer(TranslatableModelSerializer):
    translations = TranslatedFieldsField(shared_model=Course)
    modules = ModuleSerializer(many=True, read_only=True)

    class Meta:
        model = Course
        fields = ['id', 'subject', 'translations', 'slug',
                  'created', 'owner', 'modules']
