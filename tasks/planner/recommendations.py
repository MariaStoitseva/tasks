from datetime import timedelta
from django.utils import timezone
from .smart_logic import generate_schedule


def generate_recommendations(tasks, daily_plan=None):
    """Rule-based recommendations aligned with the generated daily schedule."""
    now = timezone.now()
    pending_tasks = [task for task in tasks if task.status != "completed"]

    if not pending_tasks:
        return [{
            "type": "success",
            "title": "All caught up!",
            "message": "You have no active tasks. Great work!",
        }]

    recommendations = []
    overdue_tasks = [task for task in pending_tasks if task.deadline < now]
    if overdue_tasks:
        recommendations.append({
            "type": "danger",
            "title": "Overdue tasks",
            "message": (
                f"You have {len(overdue_tasks)} overdue task(s). "
                "Review or reschedule them; they are not included in the current work plan."
            ),
        })

    # The day plan is the source of truth for Today's Focus.
    today_key = timezone.localdate().isoformat()
    today_plan = next(
        (day for day in (daily_plan or []) if str(day.get("date")) == today_key),
        None,
    )
    if today_plan and today_plan.get("tasks"):
        parts = [
            f"{item['title']} ({float(item['hours']):g} h)"
            for item in today_plan["tasks"]
        ]
        recommendations.append({
            "type": "primary",
            "title": "Today's Focus",
            "message": "Your plan for today: " + ", ".join(parts) + ".",
        })
    elif daily_plan is not None:
        recommendations.append({
            "type": "info",
            "title": "Today's Focus",
            "message": "No work sessions are scheduled for today.",
        })

    urgent_tasks = [
        task for task in pending_tasks
        if now <= task.deadline <= now + timedelta(days=2)
    ]
    if urgent_tasks:
        recommendations.append({
            "type": "warning",
            "title": "Upcoming deadlines",
            "message": f"You have {len(urgent_tasks)} task(s) due within 48 hours.",
        })

    total_hours = sum(float(task.estimated_hours or 0) for task in pending_tasks)
    if total_hours > 20:
        recommendations.append({
            "type": "info",
            "title": "High workload",
            "message": (
                f"You have {total_hours:g} estimated hours remaining "
                "across active tasks. Consider smaller work sessions."
            ),
        })

    # Fallback only for callers that do not provide a daily plan.
    if daily_plan is None:
        schedule = generate_schedule(pending_tasks)
        if schedule:
            recommendations.append({
                "type": "primary",
                "title": "Suggested next task",
                "message": f"Consider reviewing '{schedule[0].title}' next.",
            })

    return recommendations
