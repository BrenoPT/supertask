import random


def initializeTable(cursor):
    cursor.execute(
        "CREATE TABLE IF NOT EXISTS tasks (id INTEGER PRIMARY KEY, name TEXT, desc TEXT, completed INTERGER DEFAULT 0, due_date TEXT)"
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

    print(random.choice(greetings))


def checkNearDue(cursor):
    cursor.execute(
        "SELECT name, due_date FROM tasks WHERE due_date IS NOT NULL AND completed = 0 AND due_date <= DATE('now', '+2 days')"
    )
    tasks = cursor.fetchall()
    if not tasks:
        return
    print("\nTasks due soon!")
    for task in tasks:
        print(f"[{task[0]}] {task[1]}")


def addTask(cursor, con):
    print("\nEnter task name:")
    name = input()
    print("Enter task description:")
    desc = input()
    print("enter a due date YYYY-MM-DD (empty for no due date):")
    due_date = input()
    cursor.execute(
        "INSERT INTO tasks (name, desc, due_date) VALUES (?, ?, ?)",
        (name, desc, due_date),
    )
    con.commit()


def listTasks(cursor):
    cursor.execute("SELECT name, desc, due_date FROM tasks WHERE completed = 0")
    tasks = cursor.fetchall()
    if not tasks:
        print("\nNo pending tasks.")
        return
    for i, task in enumerate(tasks, 1):
        print(f"\n{i}. [{task[0]}]")
        print(f"   {task[1]}")
        print(f"   Due by: {task[2]}")


def completeTask(cursor, con):
    print("\nSelect task to complete:")
    cursor.execute("SELECT id, name FROM tasks WHERE completed = 0")
    for task in cursor.fetchall():
        print(f"[{task[0]}] {task[1]}")
    print("Enter task ID to complete:")
    task_id = input()
    cursor.execute("UPDATE tasks SET completed = 1 WHERE id = ?", (task_id,))
    con.commit()


def deleteTask(cursor, con):
    print("\nSelect task to delete:")
    cursor.execute("SELECT id, name FROM tasks WHERE completed = 0")
    for task in cursor.fetchall():
        print(f"[{task[0]}] {task[1]}")
    print("Enter task ID to delete:")
    task_id = input()
    cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    con.commit()
