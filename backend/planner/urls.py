from django.urls import path
from .views import views, auth_views
from django.contrib.auth.views import LogoutView

urlpatterns = [
    # ----------------------------
    # Home & Pages
    # ----------------------------
    path('', views.index, name='index'),
    path('about/', views.about, name='about'),
    path('calender/', views.calender, name='calender'),
    path('features/', views.features, name='features'),
    path('forgotpassword/', views.forgotpassword, name='forgotpassword'),
    path('signup/', views.signup, name='signup'),
    path('login/', views.login_view, name='login'),  # Updated view name
    path('logout/', views.logout_view, name='logout'),  # Using custom logout view
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/', views.profile, name='profile'),
    path('progress/', views.progress, name='progress'),
    path('tasklist/', views.tasklist, name='tasklist'),

    # ----------------------------
    # Task APIs (User-specific)
    # ----------------------------
    path('tasks/', views.tasks_list, name='tasks_list'),                          # GET all tasks of logged-in user
    path('tasks/create/', views.create_task, name='create_task'),                # POST create task (user attached)
    path('tasks/update/<int:task_id>/', views.update_task, name='update_task'),  # PUT update task (only owner)
    path('tasks/delete/<int:task_id>/', views.delete_task, name='delete_task'),  # DELETE task (only owner)

    # ----------------------------
    # Personalized Study Plan
    # ----------------------------
    path('studyplan/', views.study_plan, name='study_plan'),

    # ----------------------------
    # Reminders
    # ----------------------------
    path('reminders/', views.reminders, name='reminders'),

    # ----------------------------
    # Local Notifications
    # ----------------------------
    path('notifications/', views.notifications, name='notifications'),

    # ----------------------------
    # Email Notifications
    # ----------------------------
    path('send-email-notifications/', views.send_email_notifications, name='send_email_notifications'),

    # ----------------------------
    # Authentication APIs (REST)
    # ----------------------------
    path('api/signup/', auth_views.signup, name='api_signup'),   # POST signup
    path('api/login/', auth_views.login_view, name='api_login'), # POST login (updated view name)
    path('api/logout/', auth_views.logout_view, name='api_logout'), # POST logout (Token required)
]
