# Supertask ⚡

A minimal command-line to-do app. Add, list, complete, and delete tasks with optional due dates, stored locally in a SQLite database!

---

## Dependencies 📦

- Python 3.10+
- [pipx](https://pipx.pypa.io/) (for installation)

---

## Installation 🚀

**1. Clone the repository:**
```bash
git clone https://github.com/youruser/supertask.git
cd supertask/app
```

**2. Install with pipx:**
```bash
pipx install .
```

---

## Usage 📖

Run the app from anywhere in your terminal:
```bash
st
```

| Command      | Key |
|--------------|-----|
| Add task     | `a` |
| List tasks   | `l` |
| Complete task| `c` |
| Delete task  | `d` |
| History      | `h` |
| Quit         | `q` |

Due dates support natural language like `tomorrow`, `next friday`, or `2026-12-01 14:00`!
