
from datetime import timedelta
from decimal import Decimal

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .forms import TaskForm
from .models import Task
from .smart_logic import (
    calculate_priority,
    generate_schedule,
)


class TaskTests(TestCase):

    def setUp(self):
        self.task = Task.objects.create(
            title="University Assignment",
            description="Complete the project",
            deadline=timezone.now() + timedelta(days=5),
            estimated_hours=Decimal("4.0"),
            category="university",
            importance="high",
        )

    def test_task_creation(self):
        self.assertEqual(Task.objects.count(), 1)
        self.assertEqual(
            self.task.title,
            "University Assignment"
        )
        self.assertEqual(self.task.status, "pending")

    def test_task_form_valid(self):
        form = TaskForm(data={
            "title": "New Task",
            "description": "Test description",
            "deadline": (
                timezone.localtime()
                + timedelta(days=3)
            ).strftime("%Y-%m-%dT%H:%M"),
            "estimated_hours": "2.5",
            "category": "personal",
            "importance": "medium",
        })

        self.assertTrue(form.is_valid(), form.errors)

    def test_create_task_view(self):
        response = self.client.post(
            reverse("create_task"),
            data={
                "title": "Created Through View",
                "description": "Test",
                "deadline": (
                    timezone.localtime()
                    + timedelta(days=3)
                ).strftime("%Y-%m-%dT%H:%M"),
                "estimated_hours": "2.5",
                "category": "work",
                "importance": "medium",
            }
        )

        self.assertRedirects(
            response,
            reverse("dashboard")
        )

        self.assertTrue(
            Task.objects.filter(
                title="Created Through View"
            ).exists()
        )

    def test_edit_task(self):
        response = self.client.post(
            reverse("edit_task", args=[self.task.id]),
            data={
                "title": "Updated Assignment",
                "description": "Updated description",
                "deadline": (
                    timezone.localtime()
                    + timedelta(days=5)
                ).strftime("%Y-%m-%dT%H:%M"),
                "estimated_hours": "6.0",
                "category": "university",
                "importance": "high",
            }
        )

        self.assertRedirects(
            response,
            reverse("task_list")
        )

        self.task.refresh_from_db()

        self.assertEqual(
            self.task.title,
            "Updated Assignment"
        )

        self.assertEqual(
            self.task.estimated_hours,
            Decimal("6.0")
        )

    def test_delete_task(self):
        response = self.client.post(
            reverse("delete_task", args=[self.task.id])
        )

        self.assertRedirects(
            response,
            reverse("task_list")
        )

        self.assertFalse(
            Task.objects.filter(id=self.task.id).exists()
        )

    def test_start_and_pause_task(self):
        self.client.post(
            reverse("start_task", args=[self.task.id])
        )

        self.task.refresh_from_db()
        self.assertEqual(self.task.status, "in_progress")

        self.client.post(
            reverse("pause_task", args=[self.task.id])
        )

        self.task.refresh_from_db()
        self.assertEqual(self.task.status, "pending")

    def test_complete_task(self):
        self.client.post(
            reverse("complete_task", args=[self.task.id])
        )

        self.task.refresh_from_db()

        self.assertEqual(self.task.status, "completed")
        self.assertIsNotNone(self.task.completed_at)

    def test_priority_calculation(self):
        self.task.deadline = (
            timezone.now() + timedelta(hours=12)
        )
        self.task.importance = "high"
        self.task.estimated_hours = Decimal("8.0")

        priority = calculate_priority(self.task)

        self.assertEqual(priority, "critical")

    def test_completed_tasks_not_scheduled(self):
        self.task.status = "completed"

        schedule = generate_schedule(
            [self.task],
            daily_capacity=8
        )

        self.assertEqual(len(schedule), 0)

    def test_daily_capacity_not_exceeded(self):
        second_task = Task.objects.create(
            title="Second Assignment",
            deadline=timezone.now() + timedelta(days=3),
            estimated_hours=Decimal("8.0"),
            importance="high",
        )

        schedule = generate_schedule(
            [self.task, second_task],
            daily_capacity=4
        )

        daily_totals = {}

        for task in schedule:
            for session in task.daily_plan:
                day = session["date"]

                daily_totals[day] = (
                    daily_totals.get(day, 0)
                    + session["hours"]
                )

        for total in daily_totals.values():
            self.assertLessEqual(total, 4)

    def test_overdue_task_not_scheduled(self):
        self.task.deadline = (
            timezone.now() - timedelta(days=2)
        )

        schedule = generate_schedule(
            [self.task],
            daily_capacity=8
        )

        self.assertEqual(
            schedule[0].daily_plan,
            []
        )

        self.assertEqual(
            schedule[0].unscheduled_hours,
            4.0
        )

    def test_statistics_includes_in_progress_overdue(self):
        self.task.status = "in_progress"
        self.task.deadline = (
            timezone.now() - timedelta(days=1)
        )
        self.task.save()

        response = self.client.get(
            reverse("statistics")
        )

        self.assertEqual(response.status_code, 200)

        self.assertEqual(
            response.context["overdue_tasks"],
            1
        )

        self.assertEqual(
            response.context["in_progress_tasks"],
            1
        )

    def test_invalid_capacity_uses_default(self):
        response = self.client.get(
            reverse("smart_planner"),
            {"capacity": "invalid"}
        )

        self.assertEqual(response.status_code, 200)

        self.assertEqual(
            response.context["daily_capacity"],
            8.0
        )
