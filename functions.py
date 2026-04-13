import os
import random
from sqlite3 import PARSE_DECLTYPES

import dateparser
from colorama import Fore


def initializeTable(cursor):
    cursor.execute(
        "CREATE TABLE IF NOT EXISTS tasks (id INTEGER PRIMARY KEY, name TEXT, desc TEXT, completed INTERGER DEFAULT 0, due_date TEXT DEFAULT NULL)"
    )


def printGreeting():
    greetings = [
        "Welcome Back!",
        "Here We Go Again!",
        "Let's Do It!",
        "We Missed You!",
        "Hey There!",
        "Oh, Uh.. Hi!",
        "How Did You Get Here?",
        "To Do, Or Not To Do, That Is The Question.",
        "To Do Today!",
        "[Pink Panther Theme]",
        "Supertask!",
        "Why Do Today What Can Be Done Tomorrow?",
        "Today Is The Day!",
        "Gosh... Finally!",
        "I Was Wondering Where You Were!",
        ":3",
        "Hi.",
        "diinki!",
        "Bogos Binted?",
        "Are You New Here?",
        "Where Were We?",
    ]

    print(Fore.GREEN + "\n" + random.choice(greetings))


def checkNearDue(cursor):
    cursor.execute(
        "SELECT name, due_date FROM tasks WHERE due_date IS NOT NULL AND completed = 0 AND due_date <= datetime('now', '+2 days')"
    )
    tasks = cursor.fetchall()
    if not tasks:
        return
    print(Fore.YELLOW + "\nTasks due soon!")
    for task in tasks:
        print(f"[{task[0]}] {task[1]}")


def addTask(cursor, con):
    os.system("cls" if os.name == "nt" else "clear")
    print("\nEnter task name:")
    name = input().strip()
    if not name:
        print("Task name cannot be empty.")
        return
    print("Enter task description:")
    desc = input().strip()
    print("Enter a due date (empty for none):")
    dueDate = input()
    parsed = dateparser.parse(dueDate) if dueDate else None
    parsedDueDate = parsed.strftime("%Y-%m-%d %H:%M") if parsed else None
    cursor.execute(
        "INSERT INTO tasks (name, desc, due_date) VALUES (?, ?, ?)",
        (name, desc, parsedDueDate),
    )
    con.commit()
    os.system("cls" if os.name == "nt" else "clear")
    print("Task added successfully.")


def listTasks(cursor):
    os.system("cls" if os.name == "nt" else "clear")
    cursor.execute("SELECT name, desc, due_date FROM tasks WHERE completed = 0")
    tasks = cursor.fetchall()
    if not tasks:
        print("\nNo pending tasks.")
        return
    for i, task in enumerate(tasks, 1):
        print(f"\n{i}. [{task[0]}]")
        print(f"   {task[1]}")
        print(f"   Due: {task[2] if task[2] else 'No due date'}")


def completeTask(cursor, con):
    os.system("cls" if os.name == "nt" else "clear")
    print("\nSelect task to complete:")
    cursor.execute("SELECT id, name FROM tasks WHERE completed = 0")
    tasks = cursor.fetchall()
    validIds = {str(row[0]) for row in tasks}
    for task in tasks:
        print(f"[{task[0]}] {task[1]}")
    print("Enter one or more task ID to complete:")
    taskIds = input().strip().split()
    if not taskIds:
        print("No IDs entered.")
        return
    notFound = [tid for tid in taskIds if tid not in validIds]
    if notFound:
        print(f"Invalid IDs: {', '.join(notFound)}.")
        print("Nothing updated.")
        return
    for taskId in taskIds:
        cursor.execute("UPDATE tasks SET completed = 1 WHERE id = ?", (taskId,))
    con.commit()
    os.system("cls" if os.name == "nt" else "clear")
    print("Task completed successfully.")


def deleteTask(cursor, con):
    os.system("cls" if os.name == "nt" else "clear")
    print("\nSelect task to delete:")
    cursor.execute("SELECT id, name FROM tasks WHERE completed = 0")
    tasks = cursor.fetchall()
    validIds = {str(row[0]) for row in tasks}
    for task in tasks:
        print(f"[{task[0]}] {task[1]}")
    print("Enter one or more task ID to delete:")
    taskIds = input().strip().split()
    if not taskIds:
        print("No IDs entered.")
        return
    notFound = [tid for tid in taskIds if tid not in validIds]
    if notFound:
        print(f"Invalid IDs: {', '.join(notFound)}.")
        print("Nothing deleted.")
        return
    for taskId in taskIds:
        cursor.execute("DELETE FROM tasks WHERE id = ?", (taskId,))
    con.commit()
    os.system("cls" if os.name == "nt" else "clear")
    print(f"{len(taskIds)} task(s) deleted successfully.")
