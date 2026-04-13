import sqlite3

import functions
from colorama import Fore

con = sqlite3.connect("todo.db")
cursor = con.cursor()

if (
    cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='tasks'"
    ).fetchone()
    is None
):
    functions.initializeTable(cursor)

functions.printGreeting()

while True:
    functions.checkNearDue(cursor)

    print(Fore.WHITE + "\nWhat do you wanna do?")

    print(Fore.BLUE + f"{'add':<12}a")
    print(f"{'list':<12}l")
    print(f"{'complete':<12}c")
    print(f"{'delete':<12}d")
    print(f"{'quit':<12}q")

    command = input(Fore.WHITE + ">>> ").lower()
    match command:
        case "add" | "a":
            functions.addTask(cursor, con)
        case "list" | "l":
            functions.listTasks(cursor)
        case "complete" | "c":
            functions.completeTask(cursor, con)
        case "delete" | "d":
            functions.deleteTask(cursor, con)
        case "quit" | "q":
            break
        case _:
            print("Invalid command")

con.close()
