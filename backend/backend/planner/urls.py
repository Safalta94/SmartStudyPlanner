from django.urls import path
from .views import views, auth_views

urlpatterns = [
    # Home
    path('', views.home, name='home'),

    # Task APIs
    path('tasks/', views.tasks_list, name='tasks_list'),             # GET all tasks of user
    path('tasks/create/', views.create_task, name='create_task'),    # POST create task
    path('tasks/update/<int:task_id>/', views.update_task, name='update_task'),  # PUT update task
    path('tasks/delete/<int:task_id>/', views.delete_task, name='delete_task'),  # DELETE task

    # Study Plan
    path('studyplan/', views.study_plan, name='study_plan'),

    # Reminders
    path('reminders/', views.reminders, name='reminders'),

    # Local Notifications
    path('notifications/', views.notifications, name='notifications'),

    # Email Notifications
    path('send-email-notifications/', views.send_email_notifications, name='send_email_notifications'),

    # Authentication
    path('signup/', auth_views.signup, name='signup'),
    path('login/', auth_views.login, name='login'),
    path('logout/', auth_views.logout, name='logout'),
]
