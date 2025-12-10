from rest_framework.response import Response
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from datetime import date
from django.http import HttpResponse
from django.core.mail import send_mail
from ..models import Task
from ..serializers import TaskSerializer

# ----------------------------
# Home Page
# ----------------------------
def home(request):
    return HttpResponse("Welcome to Smart Study Planner API")

# ----------------------------
# Step 5 — GET Tasks (User’s Own Tasks)
# ----------------------------
@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def tasks_list(request):
    tasks = Task.objects.filter(user=request.user)  # Only current user's tasks
    serializer = TaskSerializer(tasks, many=True)
    return Response(serializer.data)

# ----------------------------
# Step 4 — Create Task
# ----------------------------
@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def create_task(request):
    data = request.data
    serializer = TaskSerializer(data=data)

    if serializer.is_valid():
        serializer.save(user=request.user)  # Attach logged-in user
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# ----------------------------
# Step 6 — Update Task
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
# Step 7 — Delete Task
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
# Personalized Study Plan
# ----------------------------
@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def study_plan(request):
    tasks = Task.objects.filter(user=request.user, completed=False)
    sorted_tasks = sorted(tasks, key=lambda t: (t.due_date, t.priority, -t.difficulty))

    plan_data = []
    today = date.today()
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
# Reminders
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
# Local Notifications
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
# Email Notifications
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
