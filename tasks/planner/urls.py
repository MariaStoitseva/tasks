from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('tasks/create/', views.create_task, name='create_task'),
    path('tasks/', views.task_list, name='task_list'),
    path('tasks/<int:task_id>/delete/', views.delete_task, name='delete_task'),
    path('tasks/<int:task_id>/edit/', views.edit_task, name='edit_task'),
    path('tasks/<int:task_id>/complete/', views.complete_task, name='complete_task'),
    path('tasks/<int:task_id>/start/', views.start_task, name='start_task'),
    path('tasks/<int:task_id>/pause/', views.pause_task, name='pause_task'),
    path('smart-planner/', views.smart_planner, name='smart_planner'),
    path('calendar/', views.calendar_view, name='calendar'),
    path('statistics/', views.statistics_view, name='statistics'),
]
