def main():
    import os
    import sqlite3

    from colorama import Fore

    from . import functions

    con = sqlite3.connect(functions.getDbPath())
    cursor = con.cursor()

    # create tasks table if it doesn't exist
    if (
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='tasks'"
        ).fetchone()
        is None
    ):
        functions.initializeTable(cursor)

    functions.printGreeting()

    while True:
        # get amount of pending tasks and display it in the prompt if any
        pendingTasks = functions.getAmountOfTasks(cursor)
        displayTasks = f"({pendingTasks})" if pendingTasks else ""

        functions.checkDue(cursor)

        print(Fore.BLUE + "\nWhat do you wanna do?" + Fore.WHITE)

        print(f"{'add':<12}" + Fore.MAGENTA + "a" + Fore.WHITE)
        print(f"{'list':<12}" + Fore.MAGENTA + "l" + Fore.WHITE + f" {displayTasks}")
        print(f"{'complete':<12}" + Fore.MAGENTA + "c" + Fore.WHITE)
        print(f"{'delete':<12}" + Fore.MAGENTA + "d" + Fore.WHITE)
        print(f"{'history':<12}" + Fore.MAGENTA + "h" + Fore.WHITE)
        print(f"{'quit':<12}" + Fore.MAGENTA + "q" + Fore.WHITE)

        command = input(">>> ").lower()
        match command:
            case "add" | "a":
                functions.addTask(cursor, con)
            case "list" | "l":
                functions.listTasks(cursor)
            case "complete" | "c":
                functions.completeTask(cursor, con)
            case "delete" | "d":
                functions.deleteTask(cursor, con)
            case "history" | "h":
                functions.printHistory(cursor)
            case "quit" | "q":
                break
            case _:
                os.system("cls" if os.name == "nt" else "clear")
                print(Fore.YELLOW + "Invalid command" + Fore.WHITE)

    con.close()
    functions.printGoodbye()


if __name__ == "__main__":
    main()
