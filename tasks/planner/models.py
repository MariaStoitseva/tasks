from django.db import models


class Task(models.Model):
    CATEGORY_CHOICES = [
        ('university', 'University'),
        ('work', 'Work'),
        ('personal', 'Personal'),
        ('other', 'Other'),
    ]

    IMPORTANCE_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ]

    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    deadline = models.DateTimeField()

    estimated_hours = models.DecimalField(
        max_digits=5,
        decimal_places=1
    )

    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        default='personal'
    )

    importance = models.CharField(
        max_length=10,
        choices=IMPORTANCE_CHOICES,
        default='medium'
    )

    priority = models.CharField(
        max_length=10,
        choices=PRIORITY_CHOICES,
        default='low'
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.title