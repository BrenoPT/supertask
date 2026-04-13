import sqlite3

import functions

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
functions.checkNearDue(cursor)

while True:
    print("\nWhat do you wanna do?")
    command = input("(add, list, complete, delete, exit):").lower()
    match command:
        case "add" | "a":
            functions.addTask(cursor, con)
        case "list" | "l":
            functions.listTasks(cursor)
        case "complete" | "c":
            functions.completeTask(cursor, con)
        case "delete" | "d":
            functions.deleteTask(cursor, con)
        case "exit" | "e":
            break
        case _:
            print("Invalid command")
