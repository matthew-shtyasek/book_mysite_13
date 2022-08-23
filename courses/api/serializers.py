from parler_rest.fields import TranslatedFieldsField
from parler_rest.serializers import TranslatableModelSerializer

from courses.models import Subject


class SubjectSerializer(TranslatableModelSerializer):
    translations = TranslatedFieldsField(shared_model=Subject)

    class Meta:
        model = Subject
        fields = ['id', 'translations', 'slug']
