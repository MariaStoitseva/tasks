# SmartTask – Intelligent Task Management System

## Live Demo

[Open SmartTask](https://smarttask-gmxq.onrender.com)

Note: The application is hosted on Render's free plan.
The first request may take up to a minute due to cold start.

SmartTask is a web-based task management application developed as a university course project using Django and PostgreSQL.

The application helps users organize tasks, manage deadlines, track progress, and create personalized work schedules through a rule-based Smart Planner.

## Features

- **Task Management:** Create, view, edit, and delete tasks.
- **Task Statuses:** Manage tasks using Pending, In Progress, and Completed statuses.
- **Automatic Priority Calculation:** Assigns Low, Medium, High, or Critical priority based on task importance, deadline, and estimated workload.
- **Smart Planner:** Automatically distributes tasks across available days while respecting deadlines and a shared daily working capacity.
- **Adjustable Daily Capacity:** Choose between 1 and 12 working hours per day, with 8 hours as the default.
- **Daily and Weekly Views:** Navigate through planned work sessions.
- **AI Recommendations:** Rule-based suggestions for overdue tasks, approaching deadlines, and workload management.
- **Calendar:** Visualize upcoming tasks and deadlines.
- **Statistics:** Monitor completion rates, overdue tasks, task statuses, and category distribution.
- **Dashboard:** View key task metrics and upcoming deadlines.

## Technologies

- Python 3.12+
- Django 6.1.1
- PostgreSQL
- HTML5 and CSS3
- Bootstrap 5
- JavaScript
- Chart.js
- FullCalendar

## Smart Planner Logic

SmartTask uses a rule-based scheduling algorithm rather than an external AI service or machine learning model.

The algorithm:

1. Calculates task priority using importance, deadline proximity, and estimated working hours.
2. Orders active tasks primarily by deadline.
3. Distributes estimated working hours across available days.
4. Applies a shared daily working capacity across all tasks.
5. Identifies tasks that cannot be fully scheduled before their deadlines.
6. Generates recommendations based on task urgency and workload.

Overdue tasks are excluded from the daily schedule and flagged for review or rescheduling.

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/SmartTask.git
cd SmartTask
```

Replace `YOUR_USERNAME` with the repository owner's GitHub username.

### 2. Create and activate a virtual environment

```bash
python -m venv .venv
```

On Windows:

```bash
.venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure PostgreSQL

Create a PostgreSQL database named `smarttask_db`.

Create a `.env` file in the same directory as `manage.py`:

```dotenv
DJANGO_SECRET_KEY=your-secret-key
DJANGO_DEBUG=True

DB_NAME=smarttask_db
DB_USER=postgres
DB_PASSWORD=your-postgresql-password
DB_HOST=localhost
DB_PORT=5432
```

Replace the example values with your local configuration. Do not commit `.env` to GitHub.

### 5. Apply database migrations

```bash
python manage.py migrate
```

### 6. Run the development server

```bash
python manage.py runserver
```

Open the application at:

http://127.0.0.1:8000/

## Running Tests

SmartTask includes automated tests covering task management, status transitions, priority calculation, scheduling capacity, overdue tasks, and statistics.

Run the tests using:

```bash
python manage.py test tasks.planner
```

## Project Purpose

This project demonstrates practical application of Django, relational databases, web development, CRUD operations, and algorithm-based task scheduling.

SmartTask was developed as part of a university software development course.

## Author

Maria Stoitseva

Plovdiv University "Paisii Hilendarski"

Bachelor's Programme: Software Technologies and Design