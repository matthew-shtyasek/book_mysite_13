from django.conf import settings
from django.forms import Form
from django.http import Http404
from django.utils import translation
from django.views.generic.base import TemplateResponseMixin, View
from django.views.generic.edit import ModelFormMixin
from parler.views import TranslatableCreateView, TranslatableUpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy, reverse
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, FormView

from courses.forms import ModuleFormSet
from courses.models import Course
from courses.templatetags.change_lang import change_lang



# todo: maybe remove
def get_course_on_any_language(pk, request, language=None):
    if language:
        _course = get_course_or_none(pk, request, language)
        if _course:
            _course.set_current_language(language)
            return _course

    for lang in settings.LANGUAGES:
        _course = get_course_or_none(pk, request, lang[0])
        if _course:
            _course.set_current_language(lang[0])
            return _course

    raise Http404()


def get_course_or_none(pk, request, language):
    successful = True
    try:
        return Course.objects.get(translations__language_code=language,
                                  pk=pk)
    except Course.DoesNotExist:
        successful = False
    finally:
        if successful:
            translation.activate(language)
            request.LANGUAGE_CODE = language
    return None


class OwnerMixin(object):
    def get_queryset(self):
        qs = super(OwnerMixin, self).get_queryset()
        return qs.filter(owner=self.request.user)


class OwnerEditMixin(object):
    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super(OwnerEditMixin, self).form_valid(form)


class OwnerCourseMixin(OwnerMixin, LoginRequiredMixin):
    model = Course
    fields = ['subject', 'title', 'slug', 'overview']
    success_url = reverse_lazy('courses:manage_list')
    template_name = 'courses/manage/course/list.html'


class OwnerCourseEditMixin(OwnerCourseMixin, OwnerEditMixin):
    template_name = 'courses/manage/course/form.html'
    object = None

    def get_form(self, form_class=None, course=None, initial=None):
        form = super(OwnerCourseEditMixin, self).get_form(form_class)
        if course:
            form.initial = {
                'subject': course.subject,
                'title': course.title,
                'slug': course.slug,
                'overview': course.overview,
            }
        if initial:
            if not form.initial:
                form.initial = dict()
            form.initial.update(initial)
        return form

    # def form_valid(self, form):
    #     self.object = form.save(commit=False)
    #     self.object.owner = self.request.user
    #     # self.object.translations
    #     form.save()
    #     return super(OwnerCourseEditMixin, self).form_valid(form)
    def form_valid(self, form):
        language = translation.get_language()
        _course = form.save(commit=False)
#
        try:
            course = Course.objects.get(pk=_course.id)
        except Course.DoesNotExist:
            course = Course()
            course.owner = self.request.user
        course.set_current_language(language)
#
        cd = form.cleaned_data
        course.subject = cd['subject']
        course.title = cd['title']
        course.slug = cd['slug']
        course.overview = cd['overview']
        course.save()
        return redirect(reverse('courses:manage_list'))


class ManageCourseListView(OwnerCourseMixin, ListView):
    template_name = 'courses/manage/course/list.html'


class CourseCreateView(PermissionRequiredMixin, OwnerCourseEditMixin, TranslatableCreateView):
    permission_required = 'courses.add_course'

    #def get(self, request, *args, **kwargs):
    #    request.DEFAULT_LANGUAGE = self.get_language()
    #    return super().get(request, *args, **kwargs)


class CourseUpdateView(PermissionRequiredMixin, OwnerCourseEditMixin, TranslatableUpdateView):
    permission_required = 'courses.change_course'
    object = Course()

    def get(self, request, *args, **kwargs):
        language = translation.get_language()
        try:
            course = Course.objects.get(translations__language_code=language, pk=kwargs.get('pk'))
            form = self.get_form(super().form_class, course)
        except Course.DoesNotExist:
            course = Course.objects.get(pk=kwargs.get('pk'))
            form = self.get_form(super().form_class, initial={'subject': course.subject})

        # form.instance = course
        # form.data = course
        context = {
            'object': course,
            'form': form,
        }
        context.update(kwargs)
        return render(request, self.template_name, context=context)


class CourseDeleteView(PermissionRequiredMixin, OwnerCourseMixin, DeleteView):
    template_name = 'courses/manage/course/delete.html'
    success_url = reverse_lazy('courses:manage_list')
    permission_required = 'courses.delete_course'


# class CourseModuleUpdateView(TemplateResponseMixin, View):
#     template_name = 'courses/manage/module/formset.html'
#     course = None
#
#     def get_formset(self, data=None):
#         return ModuleFormSet(instance=self.course,
#                              data=data)
#
#     def dispatch(self, request, pk):
#         self.course = get_object_or_404(Course,
#                                         id=pk,
#                                         owner=request.user)
#         return super(CourseModuleUpdateView, self).dispatch(request, pk)
#
#     def get(self, request, *args, **kwargs):
#         formset = self.get_formset()
#         context = {
#             'course': self.course,
#             'formset': formset
#         }
#         return self.render_to_response(context)
#
#     def post(self, request, *args, **kwargs):
#         formset = self.get_formset(data=request.POST)
#         if formset.is_valid():
#             formset.save()
#             return redirect(reverse('courses:manage_list'))
#         context = {
#             'course': self.course,
#             'formset': formset
#         }
#         return self.render_to_response(context)
#