from django.urls import path

from . import views

app_name = 'politicians'

urlpatterns = [
    path('manage/', views.manage_list, name='manage'),
    path('manage/add/', views.politician_create, name='add'),
    path('manage/<int:pk>/edit/', views.politician_edit, name='edit'),
    path('manage/<int:pk>/delete/', views.politician_delete, name='delete'),
    path('', views.directory, name='directory'),
    path('<int:pk>/', views.detail, name='detail'),
]