from django.db.models import Count
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from .forms import TaskForm
from .models import Task
from .smart_logic import DAILY_WORK_CAPACITY, calculate_priority, generate_schedule, update_task_priorities
from .recommendations import generate_recommendations


def dashboard(request):
    tasks = list(Task.objects.all())

    # Refresh priorities based on current deadlines
    update_task_priorities(tasks)

    now = timezone.now()

    total_tasks = len(tasks)

    completed_tasks = sum(
        1 for task in tasks
        if task.status == 'completed'
    )

    in_progress_tasks = sum(
        1 for task in tasks
        if task.status == 'in_progress'
    )

    pending_tasks = sum(
        1 for task in tasks
        if task.status == 'pending'
    )

    overdue_tasks = sum(
        1 for task in tasks
        if task.status != 'completed'
        and task.deadline < now
    )

    completion_rate = (
        round(completed_tasks / total_tasks * 100, 1)
        if total_tasks > 0 else 0
    )

    # Upcoming active tasks, ordered by deadline
    upcoming_tasks = sorted(
        [
            task for task in tasks
            if task.status != 'completed'
            and task.deadline >= now
        ],
        key=lambda task: task.deadline
    )[:5]

    context = {
        'total_tasks': total_tasks,
        'completed_tasks': completed_tasks,
        'in_progress_tasks': in_progress_tasks,
        'pending_tasks': pending_tasks,
        'overdue_tasks': overdue_tasks,
        'completion_rate': completion_rate,
        'upcoming_tasks': upcoming_tasks,
    }

    return render(request, 'planner/dashboard.html', context)


def create_task(request):
    if request.method == 'POST':
        form = TaskForm(request.POST)

        if form.is_valid():
            task = form.save(commit=False)

            task.priority = calculate_priority(task)

            task.save()

            return redirect('dashboard')

    else:
        form = TaskForm()

    context = {
        'form': form,
    }

    return render(request, 'planner/task_create.html', context)


def task_list(request):
    tasks = list(Task.objects.all().order_by('deadline'))

    update_task_priorities(tasks)

    return render(request, 'planner/task_list.html', {
        'tasks': tasks,
    })


def delete_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)

    if request.method == 'POST':
        task.delete()
        return redirect('task_list')

    context = {
        'task': task,
    }

    return render(request, 'planner/task_delete.html', context)


def edit_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)

    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)

        if form.is_valid():
            task = form.save(commit=False)

            task.priority = calculate_priority(task)

            task.save()

            return redirect('task_list')

    else:
        form = TaskForm(instance=task)

    context = {
        'form': form,
        'task': task,
    }

    return render(request, 'planner/task_edit.html', context)


def complete_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)

    if request.method == 'POST':
        task.status = 'completed'
        task.completed_at = timezone.now()
        task.save()

    return redirect('task_list')


def start_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)

    if request.method == 'POST' and task.status == 'pending':
        task.status = 'in_progress'
        task.save(update_fields=['status'])

    return redirect('task_list')


def pause_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)

    if request.method == 'POST' and task.status == 'in_progress':
        task.status = 'pending'
        task.save(update_fields=['status'])

    return redirect('task_list')


def smart_planner(request):
    tasks = list(Task.objects.all())

    # Get selected daily capacity
    try:
        daily_capacity = float(
            request.GET.get(
                "capacity",
                DAILY_WORK_CAPACITY
            )
        )
    except (ValueError, TypeError):
        daily_capacity = DAILY_WORK_CAPACITY

    # Allowed capacity: 1-12 hours
    if daily_capacity not in range(1, 13):
        daily_capacity = DAILY_WORK_CAPACITY

    # Update task priorities
    update_task_priorities(tasks)

    # Generate schedule with selected capacity
    schedule = generate_schedule(
        tasks,
        daily_capacity=daily_capacity
    )

    # Build daily work plan
    daily_plan = {}

    for task in schedule:
        for session in task.daily_plan:
            day = session["date"]

            if day not in daily_plan:
                daily_plan[day] = {
                    "date": day,
                    "tasks": [],
                    "total_hours": 0,
                }

            daily_plan[day]["tasks"].append({
                "title": task.title,
                "hours": session["hours"],
                "priority": task.priority,
            })

            daily_plan[day]["total_hours"] += (
                session["hours"]
            )

    # Sort days chronologically
    daily_plan = [
        {
            **daily_plan[day],
            "date": day.isoformat(),
            "total_hours": round(
                daily_plan[day]["total_hours"], 2
            ),
        }
        for day in sorted(daily_plan)
    ]

    # Generate recommendations after daily plan
    recommendations = generate_recommendations(
        tasks,
        daily_plan=daily_plan
    )

    context = {
        "schedule": schedule,
        "recommendations": recommendations,
        "daily_plan": daily_plan,
        "daily_capacity": daily_capacity,
        "capacity_options": range(1, 13),
        "today": timezone.localdate(),
    }

    return render(
        request,
        "planner/smart_planner.html",
        context
    )


def calendar_view(request):
    tasks = Task.objects.exclude(status='completed')

    return render(request, 'planner/calendar.html', {
        'tasks': tasks,
    })


def statistics_view(request):
    tasks = Task.objects.all()

    total_tasks = tasks.count()
    completed_tasks = tasks.filter(status='completed').count()
    pending_tasks = tasks.filter(status='pending').count()
    in_progress_tasks = tasks.filter(status='in_progress').count()

    completion_rate = (
        round(completed_tasks / total_tasks * 100, 1)
        if total_tasks > 0 else 0
    )

    overdue_tasks = tasks.exclude(
        status='completed'
    ).filter(
        deadline__lt=timezone.now()
    ).count()

    tasks_by_category = (
        tasks.values('category')
        .annotate(count=Count('id'))
        .order_by('category')
    )

    category_labels = [
        item['category']
        for item in tasks_by_category
    ]

    category_data = [
        item['count']
        for item in tasks_by_category
    ]

    context = {
        'total_tasks': total_tasks,
        'completed_tasks': completed_tasks,
        'pending_tasks': pending_tasks,
        'in_progress_tasks': in_progress_tasks,
        'completion_rate': completion_rate,
        'overdue_tasks': overdue_tasks,
        'tasks_by_category': tasks_by_category,
        'category_labels': category_labels,
        'category_data': category_data,
    }

    return render(request, 'planner/statistics.html', context)
