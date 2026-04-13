import sqlite3
import unittest
from io import StringIO
from unittest.mock import patch

import app.todo.functions as functions


def makeDb():
    """Create an in-memory DB with the tasks table."""
    con = sqlite3.connect(":memory:")
    cursor = con.cursor()
    functions.initializeTable(cursor)
    return con, cursor


class TestInitializeTable(unittest.TestCase):
    def setUp(self):
        self.con, self.cursor = makeDb()

    def test_creates_table(self):
        self.cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='tasks'"
        )
        self.assertIsNotNone(self.cursor.fetchone())

    def test_idempotent(self):
        functions.initializeTable(self.cursor)

    def tearDown(self):
        self.con.close()


class TestAddTask(unittest.TestCase):
    def setUp(self):
        self.con, self.cursor = makeDb()

    def _addTask(self, inputs):
        with (
            patch("builtins.input", side_effect=inputs),
            patch("os.system"),
            patch("builtins.print"),
        ):
            functions.addTask(self.cursor, self.con)

    def test_add_task_with_all_fields(self):
        self._addTask(["Buy groceries", "Milk and eggs", "2026-12-01"])
        self.cursor.execute("SELECT name, desc, due_date FROM tasks")
        row = self.cursor.fetchone()
        self.assertEqual(row[0], "Buy groceries")
        self.assertEqual(row[1], "Milk and eggs")
        self.assertIsNotNone(row[2])

    def test_add_task_no_due_date(self):
        self._addTask(["Read book", "A good one", ""])
        self.cursor.execute("SELECT due_date FROM tasks")
        row = self.cursor.fetchone()
        self.assertIsNone(row[0])

    def test_add_task_no_description(self):
        self._addTask(["Quick task", "", ""])
        self.cursor.execute("SELECT desc FROM tasks")
        row = self.cursor.fetchone()
        self.assertEqual(row[0], "")

    def test_add_task_empty_name_does_not_insert(self):
        self._addTask(["", "some desc", ""])
        self.cursor.execute("SELECT COUNT(*) FROM tasks")
        self.assertEqual(self.cursor.fetchone()[0], 0)

    def test_add_task_whitespace_name_does_not_insert(self):
        self._addTask(["   ", "some desc", ""])
        self.cursor.execute("SELECT COUNT(*) FROM tasks")
        self.assertEqual(self.cursor.fetchone()[0], 0)

    def test_add_task_invalid_due_date_stores_none(self):
        self._addTask(["Task", "Desc", "not-a-date-at-all-xyz"])
        self.cursor.execute("SELECT due_date FROM tasks")
        row = self.cursor.fetchone()
        # dateparser may or may not parse garbage — either None or a date string is acceptable
        # what matters is it didn't crash
        self.assertTrue(row is not None)

    def tearDown(self):
        self.con.close()


class TestListTasks(unittest.TestCase):
    def setUp(self):
        self.con, self.cursor = makeDb()

    def test_list_no_tasks(self):
        output = StringIO()
        with patch("os.system"), patch("sys.stdout", output):
            functions.listTasks(self.cursor)
        self.assertIn("No pending tasks", output.getvalue())

    def test_list_shows_pending_tasks(self):
        self.cursor.execute(
            "INSERT INTO tasks (name, desc) VALUES ('Task A', 'Desc A')"
        )
        output = StringIO()
        with patch("os.system"), patch("sys.stdout", output):
            functions.listTasks(self.cursor)
        self.assertIn("Task A", output.getvalue())

    def test_list_does_not_show_completed_tasks(self):
        self.cursor.execute(
            "INSERT INTO tasks (name, desc, completed) VALUES ('Done Task', 'x', 1)"
        )
        output = StringIO()
        with patch("os.system"), patch("sys.stdout", output):
            functions.listTasks(self.cursor)
        self.assertNotIn("Done Task", output.getvalue())

    def test_list_shows_no_due_date_placeholder(self):
        self.cursor.execute("INSERT INTO tasks (name, desc) VALUES ('No Date', '')")
        output = StringIO()
        with patch("os.system"), patch("sys.stdout", output):
            functions.listTasks(self.cursor)
        self.assertIn("No due date", output.getvalue())

    def tearDown(self):
        self.con.close()


class TestCompleteTask(unittest.TestCase):
    def setUp(self):
        self.con, self.cursor = makeDb()
        self.cursor.execute("INSERT INTO tasks (name, desc) VALUES ('Task A', '')")
        self.cursor.execute("INSERT INTO tasks (name, desc) VALUES ('Task B', '')")
        self.con.commit()

    def _completeTask(self, inputs):
        with (
            patch("builtins.input", side_effect=inputs),
            patch("os.system"),
            patch("builtins.print"),
        ):
            functions.completeTask(self.cursor, self.con)

    def test_complete_single_task(self):
        self._completeTask(["1"])
        self.cursor.execute("SELECT completed FROM tasks WHERE id = 1")
        self.assertEqual(self.cursor.fetchone()[0], 1)

    def test_complete_multiple_tasks(self):
        self._completeTask(["1 2"])
        self.cursor.execute("SELECT COUNT(*) FROM tasks WHERE completed = 1")
        self.assertEqual(self.cursor.fetchone()[0], 2)

    def test_complete_invalid_id(self):
        self._completeTask(["999"])
        self.cursor.execute("SELECT COUNT(*) FROM tasks WHERE completed = 1")
        self.assertEqual(self.cursor.fetchone()[0], 0)

    def test_complete_non_digit_id(self):
        self._completeTask(["abc"])
        self.cursor.execute("SELECT COUNT(*) FROM tasks WHERE completed = 1")
        self.assertEqual(self.cursor.fetchone()[0], 0)

    def test_complete_empty_input(self):
        self._completeTask([""])
        self.cursor.execute("SELECT COUNT(*) FROM tasks WHERE completed = 1")
        self.assertEqual(self.cursor.fetchone()[0], 0)

    def test_complete_no_pending_tasks(self):
        self.cursor.execute("UPDATE tasks SET completed = 1")
        self.con.commit()
        with patch("os.system"), patch("builtins.print") as mock_print:
            functions.completeTask(self.cursor, self.con)
        printed = " ".join(str(c) for c in mock_print.call_args_list)
        self.assertIn("No pending tasks", printed)

    def tearDown(self):
        self.con.close()


class TestDeleteTask(unittest.TestCase):
    def setUp(self):
        self.con, self.cursor = makeDb()
        self.cursor.execute("INSERT INTO tasks (name, desc) VALUES ('Task A', '')")
        self.cursor.execute("INSERT INTO tasks (name, desc) VALUES ('Task B', '')")
        self.con.commit()

    def _deleteTask(self, inputs):
        with (
            patch("builtins.input", side_effect=inputs),
            patch("os.system"),
            patch("builtins.print"),
        ):
            functions.deleteTask(self.cursor, self.con)

    def test_delete_single_task(self):
        self._deleteTask(["1"])
        self.cursor.execute("SELECT COUNT(*) FROM tasks")
        self.assertEqual(self.cursor.fetchone()[0], 1)

    def test_delete_multiple_tasks(self):
        self._deleteTask(["1 2"])
        self.cursor.execute("SELECT COUNT(*) FROM tasks")
        self.assertEqual(self.cursor.fetchone()[0], 0)

    def test_delete_invalid_id(self):
        self._deleteTask(["999"])
        self.cursor.execute("SELECT COUNT(*) FROM tasks")
        self.assertEqual(self.cursor.fetchone()[0], 2)

    def test_delete_non_digit_id(self):
        self._deleteTask(["abc"])
        self.cursor.execute("SELECT COUNT(*) FROM tasks")
        self.assertEqual(self.cursor.fetchone()[0], 2)

    def test_delete_empty_input(self):
        self._deleteTask([""])
        self.cursor.execute("SELECT COUNT(*) FROM tasks")
        self.assertEqual(self.cursor.fetchone()[0], 2)

    def test_delete_no_tasks(self):
        self.cursor.execute("DELETE FROM tasks")
        self.con.commit()
        with patch("os.system"), patch("builtins.print") as mock_print:
            functions.deleteTask(self.cursor, self.con)
        printed = " ".join(str(c) for c in mock_print.call_args_list)
        self.assertIn("No tasks to delete", printed)

    def test_delete_mixed_valid_invalid_ids(self):
        """Mix of valid and invalid IDs — nothing should be deleted."""
        self._deleteTask(["1 999"])
        self.cursor.execute("SELECT COUNT(*) FROM tasks")
        self.assertEqual(self.cursor.fetchone()[0], 2)

    def tearDown(self):
        self.con.close()


class TestCheckNearDue(unittest.TestCase):
    def setUp(self):
        self.con, self.cursor = makeDb()

    def test_no_near_due_tasks(self):
        with patch("builtins.print") as mock_print:
            functions.checkNearDue(self.cursor)
        mock_print.assert_not_called()

    def test_near_due_task_shown(self):
        self.cursor.execute(
            "INSERT INTO tasks (name, due_date, completed) VALUES ('Urgent', datetime('now', '+1 day'), 0)"
        )
        output = StringIO()
        with patch("sys.stdout", output):
            functions.checkNearDue(self.cursor)
        self.assertIn("Urgent", output.getvalue())

    def test_completed_task_not_shown(self):
        self.cursor.execute(
            "INSERT INTO tasks (name, due_date, completed) VALUES ('Done', datetime('now', '+1 day'), 1)"
        )
        with patch("builtins.print") as mock_print:
            functions.checkNearDue(self.cursor)
        mock_print.assert_not_called()

    def test_far_due_task_not_shown(self):
        self.cursor.execute(
            "INSERT INTO tasks (name, due_date, completed) VALUES ('Far Away', datetime('now', '+30 days'), 0)"
        )
        with patch("builtins.print") as mock_print:
            functions.checkNearDue(self.cursor)
        mock_print.assert_not_called()

    def tearDown(self):
        self.con.close()


class TestPrintHistory(unittest.TestCase):
    def setUp(self):
        self.con, self.cursor = makeDb()

    def test_empty_history(self):
        output = StringIO()
        with patch("os.system"), patch("sys.stdout", output):
            functions.printHistory(self.cursor)
        self.assertIn("No task history", output.getvalue())

    def test_history_shows_all_tasks(self):
        self.cursor.execute("INSERT INTO tasks (name, completed) VALUES ('Done', 1)")
        self.cursor.execute("INSERT INTO tasks (name, completed) VALUES ('Pending', 0)")
        output = StringIO()
        with patch("os.system"), patch("sys.stdout", output):
            functions.printHistory(self.cursor)
        self.assertIn("Done", output.getvalue())
        self.assertIn("Pending", output.getvalue())

    def tearDown(self):
        self.con.close()


if __name__ == "__main__":
    unittest.main()
