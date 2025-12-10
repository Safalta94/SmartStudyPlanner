from django.db import models
from django.contrib.auth.models import User
from datetime import date
from django.utils import timezone


class Task(models.Model):
    # Priority and Difficulty Choices
    PRIORITY_CHOICES = [
        (1, 'High'),
        (2, 'Medium'),
        (3, 'Low'),
    ]

    DIFFICULTY_CHOICES = [
        (1, 'Easy'),
        (2, 'Medium'),
        (3, 'Hard'),
    ]

    # Connect task to logged-in user
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    # Task details
    title = models.CharField(max_length=100)
    description = models.TextField()
    due_date = models.DateField()

    priority = models.IntegerField(choices=PRIORITY_CHOICES, default=2)
    difficulty = models.IntegerField(choices=DIFFICULTY_CHOICES, default=2)
    estimated_time = models.IntegerField(help_text="Estimated time to complete (hours)", default=1)

    completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True) 

    # Method to check status
    def status(self):
        today = date.today()
        if self.completed:
            return "Completed"
        elif self.due_date < today:
            return "Overdue"
        elif self.due_date == today:
            return "Due Today"
        else:
            return "Pending"

    def __str__(self):
        return self.title
