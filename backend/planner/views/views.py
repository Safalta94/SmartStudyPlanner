from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from rest_framework.response import Response
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from datetime import date
from django.core.mail import send_mail

from ..models import Task
from ..serializers import TaskSerializer

# ----------------------------
# Index / Home
# ----------------------------
def index(request):
    return render(request, 'planner/index.html')

def about(request):
    return render(request, 'planner/about.html')

def calender(request):
    return render(request, 'planner/calender.html')

@login_required(login_url='login')
def dashboard(request):
    return render(request, 'planner/dashboard.html')

def features(request):
    return render(request, 'planner/features.html')

def forgotpassword(request):
    return render(request, 'planner/forgotpassword.html')

# ----------------------------
# LOGIN (Django form-based)
# ----------------------------
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            auth_login(request, user)  # Django login
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password.')

    return render(request, 'planner/login.html')

# ----------------------------
# LOGOUT
# ----------------------------
def logout_view(request):
    auth_logout(request)
    return redirect('login')

@login_required(login_url='login')
def profile(request):
    return render(request, 'planner/profile.html')

@login_required(login_url='login')
def progress(request):
    return render(request, 'planner/progress.html')

def signup(request):
    return render(request, 'planner/signup.html')

@login_required(login_url='login')
def tasklist(request):
    return render(request, 'planner/tasklist.html')

# ----------------------------
# REST API: GET Tasks (User’s Own Tasks)
# ----------------------------
@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def tasks_list(request):
    tasks = Task.objects.filter(user=request.user)
    serializer = TaskSerializer(tasks, many=True)
    return Response(serializer.data)

# ----------------------------
# REST API: Create Task
# ----------------------------
@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def create_task(request):
    serializer = TaskSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(user=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# ----------------------------
# REST API: Update Task
# ----------------------------
@api_view(['PUT'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def update_task(request, task_id):
    try:
        task = Task.objects.get(id=task_id, user=request.user)
    except Task.DoesNotExist:
        return Response({'error': 'Task not found'}, status=status.HTTP_404_NOT_FOUND)

    serializer = TaskSerializer(task, data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# ----------------------------
# REST API: Delete Task
# ----------------------------
@api_view(['DELETE'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def delete_task(request, task_id):
    try:
        task = Task.objects.get(id=task_id, user=request.user)
    except Task.DoesNotExist:
        return Response({'error': 'Task not found'}, status=status.HTTP_404_NOT_FOUND)

    task.delete()
    return Response({'message': 'Task deleted successfully'}, status=status.HTTP_200_OK)

# ----------------------------
# REST API: Personalized Study Plan
# ----------------------------
@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def study_plan(request):
    tasks = Task.objects.filter(user=request.user, completed=False)
    sorted_tasks = sorted(tasks, key=lambda t: (t.due_date, t.priority, -t.difficulty))
    today = date.today()
    plan_data = []

    for t in sorted_tasks:
        if t.due_date == today:
            status_text = "Due Today"
        elif t.due_date < today:
            status_text = "Overdue"
        else:
            status_text = f"{(t.due_date - today).days} days left"

        plan_data.append({
            "title": t.title,
            "description": t.description,
            "due_date": t.due_date,
            "priority": t.get_priority_display(),
            "difficulty": t.get_difficulty_display(),
            "estimated_time": t.estimated_time,
            "status": status_text
        })

    return Response(plan_data)

# ----------------------------
# REST API: Reminders
# ----------------------------
@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def reminders(request):
    today = date.today()
    tasks = Task.objects.filter(user=request.user, completed=False).order_by('due_date')
    reminder_list = []

    for t in tasks:
        if t.due_date <= today:
            status_text = "Due Today" if t.due_date == today else "Overdue"
            reminder_list.append({
                "title": t.title,
                "description": t.description,
                "due_date": t.due_date,
                "priority": t.get_priority_display(),
                "difficulty": t.get_difficulty_display(),
                "estimated_time": t.estimated_time,
                "status": status_text
            })

    return Response(reminder_list)

# ----------------------------
# REST API: Local Notifications
# ----------------------------
@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def notifications(request):
    today = date.today()
    tasks = Task.objects.filter(user=request.user, completed=False).order_by('due_date')
    alerts = []

    for t in tasks:
        if t.due_date <= today:
            status_text = "Due Today" if t.due_date == today else "Overdue"
            alerts.append({
                "id": t.id,
                "title": t.title,
                "status": status_text
            })

    return Response({
        "alerts_count": len(alerts),
        "alerts": alerts
    })

# ----------------------------
# REST API: Email Notifications
# ----------------------------
@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def send_email_notifications(request):
    today = date.today()
    tasks = Task.objects.filter(user=request.user, completed=False)
    sent_count = 0
    errors = []

    for t in tasks:
        if t.due_date <= today:
            status_text = "Due Today" if t.due_date == today else "Overdue"
            subject = f"📚 Task Alert: {t.title}"
            message = (
                f"Hello {request.user.username},\n\n"
                f"This is a reminder from Smart Study Planner.\n\n"
                f"Your task **{t.title}** is *{status_text}*.\n"
                f"Due Date: {t.due_date}\n"
                f"Priority: {t.get_priority_display()}\n\n"
                f"Please complete it as soon as possible.\n\n"
                f"– Smart Study Planner Team"
            )
            from_email = "safalta_dangal@jmcampus.edu.np"
            recipient_list = ["dangalsafalta94@gmail.com"]

            try:
                send_mail(subject, message, from_email, recipient_list)
                sent_count += 1
            except Exception as e:
                errors.append(str(e))

    if errors:
        return Response({
            "message": f"Emails sent: {sent_count}, but some errors occurred.",
            "errors": errors
        }, status=status.HTTP_207_MULTI_STATUS)

    return Response({
        "message": "Email notifications sent successfully!",
        "emails_sent": sent_count
    })
