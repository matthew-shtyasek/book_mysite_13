from parler_rest.fields import TranslatedFieldsField
from parler_rest.serializers import TranslatableModelSerializer
from rest_framework.relations import RelatedField
from rest_framework.serializers import ModelSerializer

from courses.models import Subject, Course, Module, Content


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


class ItemRelatedField(RelatedField):
    def to_representation(self, value):
        return value.render()


class ContentSerializer(ModelSerializer):
    item = ItemRelatedField(read_only=True)

    class Meta:
        model = Content
        fields = ['order', 'item']


class ModuleWithContentsSerializer(ModelSerializer):
    contents = ContentSerializer(many=True)

    class Meta:
        model = Module
        fields = ['order', 'title', 'description', 'contents']


class CourseWithContentsSerializer(ModelSerializer):
    modules = ModuleWithContentsSerializer(many=True)

    class Meta:
        model = Course
        fields = ['id', 'subject', 'title', 'slug', 'overview', 'created', 'owner', 'modules']
