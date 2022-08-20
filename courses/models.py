import parler.models
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from parler.models import TranslatableModel, TranslatedFields
from django.utils.translation import gettext_lazy as _

from courses.fields import OrderField


class Subject(TranslatableModel):
    translations = TranslatedFields(
        title=models.CharField(max_length=200, verbose_name=_("Title")),
        slug=models.SlugField(max_length=200, unique=True, db_index=True, verbose_name=_("Slug")),
    )

    # class Meta:
        # ordering = ['slug']

    def __str__(self):
        return self.title


class Course(TranslatableModel):
    owner = models.ForeignKey(User,
                              related_name='courses',
                              on_delete=models.CASCADE,
                              verbose_name=_("Owner"))
    subject = models.ForeignKey(Subject,
                                related_name='courses',
                                on_delete=models.CASCADE,
                                verbose_name=_("Subject"))
    translations = TranslatedFields(
        title=models.CharField(max_length=200,
                               verbose_name=_("Title")),
        overview=models.TextField(verbose_name=_("Overview")),
        slug=models.SlugField(max_length=200,
                              unique=True,
                              db_index=True,
                              verbose_name=_("Slug")),
    )
    created = models.DateTimeField(auto_now_add=True,
                                   verbose_name=_("Created"))

    class Meta:
        ordering = ['-created']

    def __str__(self):
        return self.title


class Module(TranslatableModel):
    course = models.ForeignKey(Course,
                               related_name='modules',
                               on_delete=models.CASCADE,
                               verbose_name=_("Course"))
    translations = TranslatedFields(
        title=models.CharField(max_length=200,
                               verbose_name=_("Title")),
        description=models.TextField(blank=True,
                                     verbose_name=_("Description")),
     )
    order = OrderField(blank=True,
                       for_fields=['course'],
                       verbose_name=_("Order"))

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f'{self.order}. {self.title}'


class Content(TranslatableModel):
    module = models.ForeignKey(Module,
                               related_name='contents',
                               on_delete=models.CASCADE,
                               verbose_name=_("Module"))
    content_type = models.ForeignKey(ContentType,
                                     on_delete=models.CASCADE,
                                     limit_choices_to={'model__in': (
                                         'text', 'video', 'image', 'file')},
                                     verbose_name=_("Content type"))
    object_id = models.PositiveIntegerField()
    item = GenericForeignKey('content_type', 'object_id')
    order = OrderField(blank=True,
                       for_fields=['module'],
                       verbose_name=_("Order"))

    class Meta:
        ordering = ['order']


class BaseItem(models.Model):
    owner = models.ForeignKey(User,
                              related_name='%(class)s_related',
                              on_delete=models.CASCADE,
                              verbose_name=_("Owner"))
    title = models.CharField(max_length=200,
                             verbose_name=_("Title"))
    created = models.DateTimeField(auto_now_add=True,
                                   verbose_name=_("Created"))
    updated = models.DateTimeField(auto_now=True,
                                   verbose_name=_("Updated"))

    class Meta:
        abstract = True

    def __str__(self):
        return self.title


class Text(BaseItem):
    content = models.TextField(verbose_name=_("Text"))


class File(BaseItem):
    content=models.FileField(upload_to='files',
                             verbose_name=_("File"))


class Image(BaseItem):
    content=models.ImageField(upload_to='images',
                              verbose_name=_("Image"))


class Video(BaseItem):
    content=models.URLField(verbose_name=_("Video"))
