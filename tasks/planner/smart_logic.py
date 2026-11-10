from datetime import timedelta
from django.utils import timezone


DAILY_WORK_CAPACITY = 8.0
MINIMUM_WORK_SESSION = 0.5


def calculate_priority(task):
    now = timezone.now()

    days_left = (
        task.deadline - now
    ).total_seconds() / 86400

    score = {
        "low": 1,
        "medium": 2,
        "high": 3,
    }.get(task.importance, 1)

    if days_left <= 1:
        score += 4
    elif days_left <= 3:
        score += 3
    elif days_left <= 7:
        score += 2
    else:
        score += 1

    hours = float(task.estimated_hours or 0)

    if hours >= 8:
        score += 3
    elif hours >= 4:
        score += 2
    else:
        score += 1

    if score >= 9:
        return "critical"
    elif score >= 7:
        return "high"
    elif score >= 5:
        return "medium"

    return "low"


def generate_schedule(tasks, daily_capacity=DAILY_WORK_CAPACITY):
    now = timezone.localtime()
    today = now.date()

    daily_capacity = float(daily_capacity)

    if daily_capacity <= 0:
        daily_capacity = DAILY_WORK_CAPACITY

    priority_order = {
        "critical": 0,
        "high": 1,
        "medium": 2,
        "low": 3,
    }

    active_tasks = [
        task for task in tasks
        if task.status != "completed"
    ]

    for task in active_tasks:
        task.priority = calculate_priority(task)

    active_tasks.sort(
        key=lambda task: (
            task.deadline,
            priority_order.get(task.priority, 3),
        )
    )

    # Shared daily capacity across all tasks
    available_hours = {}
    planning_days = 365

    for day_number in range(planning_days):
        day = today + timedelta(days=day_number)
        available_hours[day] = daily_capacity

    for task in active_tasks:
        remaining_hours = float(
            task.estimated_hours or 0
        )

        task.daily_plan = []
        task.planned_hours = 0.0
        task.unscheduled_hours = 0.0

        deadline_day = timezone.localtime(
            task.deadline
        ).date()

        if deadline_day < today:
            task.recommended_start = (
                "Overdue - Start immediately"
            )
            task.recommendation_reason = (
                "The deadline has already passed. "
                "Review or reschedule this task."
            )
            task.unscheduled_hours = remaining_hours
            continue

        for day, available in available_hours.items():
            if day > deadline_day:
                break

            if remaining_hours <= 0.00001:
                break

            if available <= 0:
                continue

            allocated = min(
                remaining_hours,
                available
            )

            available_hours[day] -= allocated
            remaining_hours -= allocated

            task.daily_plan.append({
                "date": day,
                "hours": round(allocated, 2),
            })

            task.planned_hours += allocated

        task.planned_hours = round(
            task.planned_hours, 2
        )

        task.unscheduled_hours = round(
            max(0, remaining_hours), 2
        )

        if task.daily_plan:
            first_day = task.daily_plan[0]["date"]

            if first_day == today:
                task.recommended_start = "Start today"
            elif first_day == today + timedelta(days=1):
                task.recommended_start = "Start tomorrow"
            else:
                task.recommended_start = (
                    f"Start on {first_day:%b %d, %Y}"
                )

            if task.unscheduled_hours > 0:
                task.recommendation_reason = (
                    f"Scheduled {task.planned_hours:g} hours, "
                    f"but {task.unscheduled_hours:g} hours "
                    "could not fit before the deadline. "
                    "Consider adjusting the deadline "
                    "or workload."
                )
            else:
                task.recommendation_reason = (
                    f"Scheduled {task.planned_hours:g} "
                    f"hours across "
                    f"{len(task.daily_plan)} day(s), "
                    f"with a shared daily capacity "
                    f"of {daily_capacity:g} hours."
                )
        else:
            task.recommended_start = (
                "No available time"
            )
            task.recommendation_reason = (
                "There is no remaining capacity "
                "before the deadline."
            )

    return active_tasks


def get_start_recommendation(task):
    if hasattr(task, "recommended_start"):
        return {
            "start": task.recommended_start,
            "reason": task.recommendation_reason,
        }

    return {
        "start": "Not scheduled",
        "reason": "Generate the schedule first.",
    }


def update_task_priorities(tasks):
    for task in tasks:
        if task.status == "completed":
            continue

        new_priority = calculate_priority(task)

        if task.priority != new_priority:
            task.priority = new_priority
            task.save(update_fields=["priority"])

    return tasks
