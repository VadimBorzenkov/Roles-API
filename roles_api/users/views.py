from functools import reduce
from operator import or_

from django.shortcuts import render, redirect
from django.views.generic.base import TemplateView
from django.views.generic.edit import UpdateView
from django.views import View
from django.contrib.auth import login
from django.contrib.auth.views import LoginView, LogoutView
from django.views.generic.base import TemplateView
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.contrib.messages.views import SuccessMessageMixin
from django.views.generic.edit import CreateView
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from django.utils.decorators import method_decorator
from django.contrib.auth.models import Group
from django.contrib.auth.decorators import permission_required


from common.views import TitleMixin
from users.models import Todo
from users.forms import Form, UserLoginForm, UserRegistrationForm


class IndexView(TitleMixin, TemplateView):
    template_name = 'users/index.html'
    tittle = 'Home'
    model = Todo
    context_object_name = 'tasks'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Определение роли пользователя
        role = 'Гость'
        if self.request.user.is_authenticated:
            if self.request.user.groups.filter(name='Администратор').exists():
                role = 'Администратор'
            elif self.request.user.groups.filter(name='Пользователь').exists():
                role = 'Пользователь'

        # Получение данных Todo
        tasks = Todo.objects.all()

        # Добавление данных в контекст
        context['role'] = role
        context['tasks'] = tasks

        return context


def delete_record(request, pk):
    record = Todo.objects.get(pk=pk)
    record.delete()
    return redirect('index')


@method_decorator(permission_required('users.change_todo', raise_exception=True), name='dispatch')
class EditRecordView(UpdateView):
    template_name = 'users/edit_record.html'
    model = Todo
    form_class = Form
    success_url = reverse_lazy('index')

    def get_object(self, queryset=None):
        return get_object_or_404(Todo, pk=self.kwargs['pk'])


@method_decorator(permission_required('users.add_todo', raise_exception=True), name='dispatch')
class AddRecordView(View):
    template_name = 'users/add_record.html'
    succsess_url = 'users/index.html'

    def get(self, request):
        form = Form()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = Form(request.POST)
        if form.is_valid():
            # Создаем запись в основной таблице
            Todo.objects.create(
                title=form.cleaned_data['title'],
                description=form.cleaned_data['description'],
                completed=form.cleaned_data['completed'],
            )

            return redirect('index')
        return render(request, self.template_name, {'form': form})


class SearchView(View):
    template_name = 'users/search.html'
    results_template_name = 'users/search_result.html'

    def get(self, request, *args, **kwargs):
        form = Form()
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = Form(request.POST)

        if form.is_valid():
            # Создаем список Q-объектов для фильтрации записей
            q_filters = []

            # Добавляем условия в список, только если соответствующее поле заполнено
            for field_name, field_value in form.cleaned_data.items():
                if field_value:
                    q_filters.append(Q(**{field_name: field_value}))

            # Исключаем результаты, если хотя бы одно условие не выполняется
            search_results = Todo.objects.all()

            if q_filters:
                # Используем оператор | для объединения Q-объектов с условием "или"
                combined_q_filters = Q()

                for q_filter in q_filters:
                    combined_q_filters |= q_filter

                search_results = search_results.filter(combined_q_filters)

            # Проверяем, есть ли результаты поиска
            if not search_results.exists():
                return render(request, self.results_template_name, {'no_results': True})

            # Возвращаем результаты поиска в шаблон
            return render(request, self.results_template_name, {'results': search_results})

        # Возвращаем форму с ошибками, если форма не прошла валидацию
        return render(request, self.template_name, {'form': form})


class UserRegistrationView(TitleMixin, SuccessMessageMixin, CreateView):
    form_class = UserRegistrationForm
    template_name = 'users/registration.html'
    success_url = reverse_lazy('login')
    success_message = 'Поздравляю! Вы успешно зарегистрировались!'
    title = 'Регистрация'


class UserLoginView(TitleMixin, LoginView):
    template_name = 'users/login.html'
    form_class = UserLoginForm
    title = 'Авторизация'

    def form_valid(self, form):
        # Выполняем аутентификацию пользователя
        login(self.request, form.get_user())

        # Получаем сессию пользователя
        session_key = self.request.session.session_key
        if not session_key:
            # Если сессия пустая, создаем новую
            self.request.session.save()
            session_key = self.request.session.session_key

        # Устанавливаем куки с уникальным значением сессии
        response = super().form_valid(form)
        response.set_cookie('session_token', session_key, secure=True)

        # Устанавливаем группы для пользователя
        user = self.request.user
        if user.is_authenticated:
            if user.username == 'admin':  # Подставьте реальное имя пользователя
                group = Group.objects.get(name='Администратор')
                user.groups.add(group)
            else:
                group = Group.objects.get(name='Пользователь')
                user.groups.add(group)

        return response


class UserLogoutView(LogoutView):
    def dispatch(self, request, *args, **kwargs):
        # Получаем текущего пользователя
        user = request.user

        # Устанавливаем роль "гостя"
        guest_group, created = Group.objects.get_or_create(name='Гость')
        user.groups.set([guest_group])

        # Вызываем метод dispatch
        response = super().dispatch(request, *args, **kwargs)

        # Удаляем cookie и перенаправляем на нужный URL
        response = HttpResponseRedirect(reverse_lazy('index'))
        response.delete_cookie('session_token')
        return response
