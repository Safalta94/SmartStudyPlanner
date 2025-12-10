from rest_framework import serializers
from .models import Task
from datetime import date

class TaskSerializer(serializers.ModelSerializer):
    # Read-only field to show task status
    status = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Task
        # Include all fields you need in API
        fields = [
            'id', 'title', 'description', 'due_date', 
            'priority', 'difficulty', 'estimated_time', 
            'completed', 'status'
        ]
        read_only_fields = ['status']  # Status is computed, not editable

    # Method to compute status dynamically
    def get_status(self, obj):
        today = date.today()
        if obj.completed:
            return "Completed"
        elif obj.due_date < today:
            return "Overdue"
        elif obj.due_date == today:
            return "Due Today"
        else:
            return "Pending"
