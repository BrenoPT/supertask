import os
import random
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path

import dateparser
from colorama import Fore, Style


def initializeTable(cursor):
    queryFetch(
        cursor,
        "CREATE TABLE IF NOT EXISTS tasks (id INTEGER PRIMARY KEY, name TEXT, desc TEXT, completed INTEGER DEFAULT 0, due_date TEXT DEFAULT NULL)",
    )


def printGreeting():
    clearScreen()
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
        "Who tASKED?",
        "Back At It!",
        "Look Who Showed Up!",
        "The Legend Returns!",
        "Ready When You Are!",
        "Let's Get This Done!",
        "Oh Boy, More Tasks!",
        "You Again? :)",
        "Rise And Grind!",
        "Another Day, Another To-Do!",
        "The Tasks Won't Do Themselves!",
        "Loading...",
        "Achievement Unlocked: Opened App!",
        "New Day, New Tasks!",
        "Let's Cook!",
        "No Tasks Were Harmed In The Making Of This App.",
        "[Elevator Music]",
        "Task Me Anything!",
        "Have You Tried Turning It Off And On Again?",
        "Initializing Grind Mode...",
        "Your Tasks Are Waiting!",
        "Careful, Some Of These Tasks Look Hungry.",
        "Drink Water!",
    ]

    print(random.choice(greetings))


def printGoodbye():
    clearScreen()
    goodbyes = [
        "See ya!",
        "Goodbye!",
        "All Done!",
        "We Did It!",
        "Supertasked!",
        "Nice Job!",
        "Later!",
        "Donzo!",
        "zzzZZZ...",
        "That Was Easy!",
        "Time To Relax!",
        "Mission Accomplished!",
        "Bye Bye!",
        "Don't Be A Stranger!",
        "Take Care!",
        "Until Next Time!",
        "Go Touch Grass!",
        "You Earned It!",
        "The Tasks Fear You!",
        "Catch You Later!",
        "Saving Progress...",
        "Rest Up!",
        "Outstanding Work!",
        "Back To Real Life!",
        "You're On A Roll!",
        "Logging Off!",
        "Tasks Defeated!",
        "Now Go Eat Something.",
        "See You On The Other Side!",
        "Adios!",
        "Powering Down...",
        "[Credits Roll]",
        "And That's A Wrap!",
        "You're Free... For Now.",
        "Drink Water Again!",
    ]
    print(random.choice(goodbyes))


def checkDue(cursor):
    tasks = queryFetch(
        cursor,
        "SELECT name, due_date FROM tasks WHERE due_date IS NOT NULL AND completed = 0 AND due_date < datetime('now', '+2 days') AND due_date >= datetime('now')",
    )

    if not tasks:
        return

    print(Fore.YELLOW + "\nTasks due soon!" + Fore.WHITE)
    for task in tasks:
        print(f"[{task[0]}] {task[1]}")

    tasks = queryFetch(
        cursor,
        "SELECT name, due_date FROM tasks WHERE due_date IS NOT NULL AND completed = 0 AND due_date < datetime('now')",
    )
    if not tasks:
        return

    print(Fore.RED + "\nOverdue tasks!" + Fore.WHITE)
    for task in tasks:
        print(f"[{task[0]}] {task[1]}")


def addTask(cursor, con):
    clearScreen()
    print("Create a New Task\n")
    print(Fore.BLUE + "Enter task name:" + Fore.WHITE)
    name = input().strip()
    if not name:
        clearScreen()
        print(Fore.RED + "Task name cannot be empty" + Fore.WHITE)
        print(Fore.YELLOW + "Task not created" + Fore.WHITE)
        return
    print(Fore.BLUE + "Enter task description:" + Fore.WHITE)
    desc = input().strip()
    print(Fore.BLUE + "Enter a due date (empty for none):" + Fore.WHITE)
    dueDate = input()
    parsed = dateparser.parse(dueDate) if dueDate else None
    parsedDueDate = parsed.strftime("%Y-%m-%d %H:%M") if parsed else ""
    if not parsed:
        print(
            Fore.YELLOW
            + "\nBeware: Date not recognized, defaulting no due date"
            + Fore.WHITE
        )
    print(Fore.BLUE + f"\nName: " + Fore.WHITE + f"{name}")
    print(Fore.BLUE + f"Description: " + Fore.WHITE + f"{desc}")
    print(Fore.BLUE + f"Due date: " + Fore.WHITE + f"{parsedDueDate}")
    print(
        Fore.BLUE
        + "Confirm task ("
        + Fore.GREEN
        + "Y"
        + Fore.BLUE
        + "/"
        + Fore.RED
        + "n"
        + Fore.BLUE
        + ")"
        + Fore.WHITE
    )
    confirm = input().strip().lower()
    if confirm != "y" and confirm != "":
        clearScreen()
        print(Fore.YELLOW + "Task not created" + Fore.WHITE)
        return

    queryFetch(
        cursor,
        "INSERT INTO tasks (name, desc, due_date) VALUES (?, ?, ?)",
        (name, desc, parsedDueDate),
    )
    con.commit()

    clearScreen()
    print(Fore.GREEN + "✓" + Fore.WHITE + " Task added successfully.")


def listTasks(cursor):
    clearScreen()
    tasks = queryFetch(
        cursor,
        "SELECT name, desc, due_date FROM tasks WHERE completed = 0",
    )
    if not tasks:
        print(Fore.GREEN + "✓" + Fore.WHITE + " All clear! Nothing left to do.")
        return

    for i, task in enumerate(tasks, 1):
        dueDateStr = task[2] if task[2] else False
        status = getDueDateColor(dueDateStr)
        print(Fore.BLUE + f"{i}. " + status + f"{task[0]}")
        print(f"   {task[1]}" if task[1] else "   (No description)")
        print(f"   {task[2] if task[2] else '(No due date)'}" + Fore.WHITE)


def getDueDateColor(dueDateStr):
    dueDate = dateparser.parse(dueDateStr) if dueDateStr else None
    now = datetime.now()
    # if no due date, return white
    if not dueDate:
        return Fore.WHITE
    # if due date is within 2 days, return yellow
    elif dueDate <= now + timedelta(days=2) and dueDate >= now:
        return Fore.YELLOW
    # if due date is past, return red
    if dueDate < now:
        return Fore.RED
    # fallback
    return Fore.WHITE


def getAmountOfTasks(cursor):
    tasks = queryFetch(cursor, "SELECT COUNT(*) FROM tasks WHERE completed = 0")[0][0]
    if tasks == 0:
        return
    return tasks


def completeTask(cursor, con):
    clearScreen()

    print(Fore.BLUE + "Select task to complete:" + Fore.WHITE)
    tasks = queryFetch(cursor, "SELECT id, name, desc FROM tasks WHERE completed = 0")

    if not tasks:
        clearScreen()
        print(Fore.GREEN + "✓" + Fore.WHITE + " All clear! Nothing left to complete.")
        return

    for i, task in enumerate(tasks, 1):
        print(f"[{i}] {task[1]}\n{task[2]}\n" if task[2] else f"[{i}] {task[1]}\n")
    print(Fore.BLUE + "Enter one or more task ID to complete:" + Fore.WHITE)

    taskIndices = input().strip().lower().split()
    if taskIndices == ["all"]:
        taskIndices = [str(i) for i in range(1, len(tasks) + 1)]
    if not taskIndices:
        clearScreen()
        print(Fore.YELLOW + "No IDs entered" + Fore.WHITE)
        return
    validIndices = {str(i) for i in range(1, len(tasks) + 1)}
    notFound = [tid for tid in taskIndices if tid not in validIndices]
    if notFound:
        clearScreen()
        print(Fore.RED + f"Invalid ID(s): {', '.join(notFound)}" + Fore.WHITE)
        print(Fore.YELLOW + "Nothing updated" + Fore.WHITE)
        return
    taskIds = [str(tasks[int(i) - 1][0]) for i in taskIndices]
    print(
        Fore.BLUE
        + f"Complete {len(taskIds)} task(s)? ("
        + Fore.GREEN
        + "Y"
        + Fore.BLUE
        + "/"
        + Fore.RED
        + "n"
        + Fore.BLUE
        + ")"
        + Fore.WHITE
    )
    confirm = input().strip().lower()
    if confirm != "y" and confirm != "":
        clearScreen()
        print(Fore.YELLOW + "Completion cancelled" + Fore.WHITE)
        return
    for taskId in taskIds:
        queryFetch(cursor, "UPDATE tasks SET completed = 1 WHERE id = ?", (taskId,))
    con.commit()

    clearScreen()
    completedTasks = [task[1] for task in tasks if str(task[0]) in taskIds]
    print(Fore.GREEN + f"✓ Completed: {', '.join(completedTasks)}" + Fore.WHITE)


def deleteTask(cursor, con):
    clearScreen()

    print(Fore.BLUE + "Select task to delete:" + Fore.WHITE)
    tasks = queryFetch(cursor, "SELECT id, name, completed FROM tasks")

    if not tasks:
        clearScreen()
        print(Fore.GREEN + "✓" + Fore.WHITE + " All clear! Nothing left to delete.")
        return

    for i, task in enumerate(tasks, 1):
        print(f"[{i}] {task[1]}")
    for task in tasks:
        status = (
            Fore.GREEN + "✓" + Fore.WHITE if task[2] else Fore.RED + "✗" + Fore.WHITE
        )
        print(Fore.WHITE + f"[{task[0]}] {task[1]} [{status}]")

    print(Fore.BLUE + "Enter one or more task ID to delete:" + Fore.WHITE)
    taskIndices = input().strip().lower().split()
    if not taskIndices:
        clearScreen()
        print(Fore.YELLOW + "No IDs entered" + Fore.WHITE)
        return
    if taskIndices == ["all"]:
        taskIds = [str(row[0]) for row in tasks]
    else:
        validIndices = {str(i) for i in range(1, len(tasks) + 1)}
        notFound = [tid for tid in taskIndices if tid not in validIndices]
        if notFound:
            clearScreen()
            print(Fore.RED + f"Invalid ID(s): {', '.join(notFound)}" + Fore.WHITE)
            print(Fore.YELLOW + "Nothing deleted" + Fore.WHITE)
            return
        taskIds = [str(tasks[int(i) - 1][0]) for i in taskIndices]
    print(
        Fore.BLUE
        + f"Delete {len(taskIds)} task(s)? ("
        + Fore.GREEN
        + "Y"
        + Fore.BLUE
        + "/"
        + Fore.RED
        + "n"
        + Fore.BLUE
        + ")"
        + Fore.WHITE
    )
    confirm = input().strip().lower()
    if confirm != "y" and confirm != "":
        clearScreen()
        print(Fore.YELLOW + "Deletion cancelled" + Fore.WHITE)
        return
    for taskIndex in taskIds:
        queryFetch(cursor, "DELETE FROM tasks WHERE id = ?", (taskIndex,))
    con.commit()

    clearScreen()
    deletedTasks = [task[1] for task in tasks if str(task[0]) in taskIds]
    print(Fore.GREEN + f"✓ Deleted: {', '.join(deletedTasks)}" + Fore.WHITE)


def printHistory(cursor):
    clearScreen()

    tasks = queryFetch(
        cursor, "SELECT id, name, completed FROM tasks ORDER BY id DESC LIMIT 20"
    )

    if not tasks:
        print("No task history")
        return

    print(Fore.BLUE + "Task History:" + Fore.WHITE)

    for task in tasks:
        status = (
            Fore.GREEN + "✓" + Fore.WHITE if task[2] else Fore.RED + "✗" + Fore.WHITE
        )
        print(f"[{task[0]}] {task[1]} [{status}]")
    total = queryFetch(cursor, "SELECT COUNT(*) FROM tasks")[0][0]

    print(Style.DIM + f"Showing 20 most recent. {total} tasks total." + Style.RESET_ALL)


def getDbPath():
    if os.name == "nt":
        base = Path(os.environ["APPDATA"])
    else:
        base = Path.home() / ".local" / "share"

    dbDir = base / "supertask"
    dbDir.mkdir(parents=True, exist_ok=True)
    return dbDir / "todo.db"


def clearScreen():
    os.system("cls" if os.name == "nt" else "clear")


def queryFetch(cursor, query, params=()):
    cursor.execute(query, params)
    return cursor.fetchall()
