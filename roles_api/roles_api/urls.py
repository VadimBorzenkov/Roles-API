"""
URL configuration for roles_api project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path

from users.views import IndexView, UserLoginView, UserRegistrationView, UserLogoutView, delete_record, EditRecordView, AddRecordView, SearchView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', IndexView.as_view(), name='index'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('registration/', UserRegistrationView.as_view(), name='registration'),
    path('logout/', UserLogoutView.as_view(), name='logout'),
    path('delete/<int:pk>/', delete_record, name='delete_record'),
    path('edit_record/<int:pk>/',
         EditRecordView.as_view(template_name='users/edit_record.html'), name='edit_record'),
    path('add_record/', AddRecordView.as_view(), name='add_record'),
    path('search/', SearchView.as_view(), name='search'),
    path('search/result', SearchView.as_view(template_name='search_result.html'),
         name='search_result'),
]
