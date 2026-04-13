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
        case "add":
            functions.addTask(cursor, con)
        case "list":
            functions.listTasks(cursor)
        case "complete":
            functions.completeTask(cursor, con)
        case "delete":
            functions.deleteTask(cursor, con)
        case "exit":
            break
        case _:
            print("Invalid command")
