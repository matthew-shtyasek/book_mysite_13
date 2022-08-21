from braces.views import CsrfExemptMixin, JsonRequestResponseMixin
from django.apps import apps
from django.conf import settings
from django.db.models import Count
from django.forms import Form, modelform_factory
from django.http import Http404
from django.utils import translation
from django.views.generic.base import TemplateResponseMixin, View
from parler.views import TranslatableCreateView, TranslatableUpdateView, TranslatableSlugMixin
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy, reverse
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView

from courses.forms import ModuleFormSet
from courses.models import Course, Module, Content, Subject
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

    def form_valid(self, form):
        language = translation.get_language()
        _course = form.save(commit=False)

        try:
            course = Course.objects.get(pk=_course.id)
        except Course.DoesNotExist:
            course = Course()
            course.owner = self.request.user
        course.set_current_language(language)

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
    object = None

    def get_object(self, queryset=None):
        try:
            object_get = Course.objects.get(pk=self.kwargs['pk'])
        except Course.DoesNotExist:
            return Http404('Course does not exist!')
        return object_get

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


class CourseModuleUpdateView(TemplateResponseMixin, View):
    template_name = 'courses/manage/module/formset.html'
    course = None

    def get_formset(self, data=None):
        return ModuleFormSet(instance=self.course,
                             data=data)

    def dispatch(self, request, pk):
        self.course = get_object_or_404(Course,
                                        id=pk,
                                        owner=request.user)
        return super(CourseModuleUpdateView, self).dispatch(request, pk)

    def get(self, request, *args, **kwargs):
        formset = self.get_formset()
        context = {
            'course': self.course,
            'formset': formset
        }
        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        formset = self.get_formset(data=request.POST)
        if formset.is_valid():
            formset.save()
            return redirect(reverse('courses:manage_list'))
        context = {
            'course': self.course,
            'formset': formset
        }
        return self.render_to_response(context)


class ContentCreateUpdateView(TemplateResponseMixin, View):
    module = None
    model = None
    obj = None
    template_name = 'courses/manage/content/form.html'

    def get_model(self, model_name):
        if model_name in ('text', 'video', 'image', 'file'):
            return apps.get_model(app_label='courses',
                                  model_name=model_name)
        return None

    def get_form(self, model, *args, **kwargs):
        form = modelform_factory(model,
                                 exclude=['owner',
                                          'order',
                                          'created',
                                          'updated'])
        return form(*args, **kwargs)

    def dispatch(self, request, module_id, model_name, id=None):
        self.module = get_object_or_404(Module,
                                        id=module_id,
                                        course__owner=request.user)
        self.model = self.get_model(model_name)
        if id:
            self.obj = get_object_or_404(self.model,
                                         id=id,
                                         owner=request.user)
        return super(ContentCreateUpdateView, self).dispatch(request, module_id, model_name, id)

    def get(self, request, *args, **kwargs):
        form = self.get_form(model=self.model, instance=self.obj)
        context = {
            'form': form,
            'object': self.obj
        }
        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        form = self.get_form(model=self.model,
                             instance=self.obj,
                             data=request.POST,
                             files=request.FILES)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.owner = request.user
            obj.save()
            if not args[2]:
                Content.objects.create(module=self.module,
                                       item=obj)
            return redirect(reverse('courses:module_content_list', args=[self.module.id]))
        context = {
            'form': form,
            'object': self.obj
        }
        return self.render_to_response(context)


class ContentDeleteView(View):
    def post(self, request, *args, **kwargs):
        content = get_object_or_404(Content,
                                    id=id,
                                    module__course__owner=request.user)
        module = content.module
        content.item.delete()
        content.delete()
        return redirect(reverse('courses:module_content_list', args=[module.id]))


class ModuleContentListView(TemplateResponseMixin, View):
    template_name = 'courses/manage/module/content_list.html'

    def get(self, request, *args, **kwargs):
        module = get_object_or_404(Module,
                                   id=kwargs['module_id'],
                                   course__owner=request.user)
        return self.render_to_response({'module': module})


class ModuleOrderView(CsrfExemptMixin, JsonRequestResponseMixin, View):
    def post(self, request):
        for id, order in self.request_json.items():
            Module.objects.filter(id=id,
                                  course__owner=request.user).update(order=order)
        return self.render_json_response({'saved': 'OK'})


class ContentOrderView(CsrfExemptMixin, JsonRequestResponseMixin, View):
    def post(self, request):
        for id, order in self.request_json.items():
            Content.objects.filter(id=id,
                                   module__course__owner=request.user).update(order=order)
        return self.render_json_response({'saved': 'OK'})


class CourseListView(TemplateResponseMixin, View):
    model = Course
    template_name = 'courses/course/list.html'

    def get(self, request, subject_slug=None):
        subjects = Subject.objects.annotate(
            total_courses=Count('courses'))
        courses = Course.objects.annotate(total_modules=Count('modules'))
        subject = None
        if subject_slug:
            language = request.LANGUAGE_CODE
            subject = get_object_or_404(Subject, translations__slug=subject_slug)
            courses = Course.objects.filter(subject=subject)
        context = {
            'subjects': subjects,
            'subject': subject,
            'courses': courses,
        }
        return self.render_to_response(context)


class CourseDetailView(TranslatableSlugMixin, DetailView):
    model = Course
    template_name = 'courses/course/detail.html'

