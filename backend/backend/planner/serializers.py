from rest_framework import serializers
from .models import Task
from datetime import date

class TaskSerializer(serializers.ModelSerializer):
    # Remove 'source' here
    status = serializers.ReadOnlyField()  

    class Meta:
        model = Task
        fields = ['id', 'title', 'description', 'due_date', 'priority', 'difficulty', 'estimated_time', 'completed', 'status']

def get_status(self, obj):
        today = date.today()
        if obj.due_date < today:
            return "Overdue"
        elif obj.due_date == today:
            return "Due Today"
        else:
            return "Upcoming"