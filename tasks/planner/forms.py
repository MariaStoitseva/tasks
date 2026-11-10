from django import forms
from .models import Task


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task

        fields = [
            'title',
            'description',
            'deadline',
            'estimated_hours',
            'category',
            'importance',
        ]

        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter task title'
            }),

            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Describe your task'
            }),

            'deadline': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),

            'estimated_hours': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.5',
                'min': '0.5'
            }),

            'category': forms.Select(attrs={
                'class': 'form-select'
            }),

            'importance': forms.Select(attrs={
                'class': 'form-select'
            }),
        }