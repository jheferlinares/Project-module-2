"""
Task & Category Management System
Module 2 - SQL Relational Databases
Author: Jhefersson Linares
"""

import os
import psycopg2
from psycopg2 import sql
from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    "host":     os.getenv("DB_HOST", "localhost"),
    "port":     os.getenv("DB_PORT", "5432"),
    "dbname":   os.getenv("DB_NAME", "taskdb"),
    "user":     os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", ""),
}

PRIORITY_LABEL = {1: "High", 2: "Medium", 3: "Low"}
STATUS_OPTIONS  = ["pending", "in_progress", "done"]


def get_connection():
    return psycopg2.connect(**DB_CONFIG)


# ── Helpers ──────────────────────────────────────────────────

def print_table(rows, headers):
    if not rows:
        print("  (no records found)")
        return
    col_widths = [max(len(str(h)), max(len(str(r[i])) for r in rows))
                  for i, h in enumerate(headers)]
    fmt = "  " + "  ".join(f"{{:<{w}}}" for w in col_widths)
    sep = "  " + "  ".join("-" * w for w in col_widths)
    print(fmt.format(*headers))
    print(sep)
    for row in rows:
        print(fmt.format(*[str(v) if v is not None else "" for v in row]))


def input_choice(prompt, options):
    while True:
        val = input(prompt).strip().lower()
        if val in options:
            return val
        print(f"  Invalid. Choose from: {options}")


def input_int(prompt, min_val=None, max_val=None):
    while True:
        try:
            val = int(input(prompt).strip())
            if (min_val is None or val >= min_val) and (max_val is None or val <= max_val):
                return val
            print(f"  Enter a number between {min_val} and {max_val}.")
        except ValueError:
            print("  Please enter a valid integer.")


# ── Category Operations ───────────────────────────────────────

def list_categories(conn):
    with conn.cursor() as cur:
        cur.execute("""
            SELECT c.id, c.name, c.description,
                   COUNT(t.id) AS task_count
            FROM categories c
            LEFT JOIN tasks t ON c.id = t.category_id
            GROUP BY c.id
            ORDER BY c.name
        """)
        rows = cur.fetchall()
    print_table(rows, ["ID", "Name", "Description", "Tasks"])


def add_category(conn):
    name = input("  Category name: ").strip()
    desc = input("  Description (optional): ").strip() or None
    with conn.cursor() as cur:
        cur.execute(
            "INSERT INTO categories (name, description) VALUES (%s, %s) RETURNING id",
            (name, desc)
        )
        new_id = cur.fetchone()[0]
    conn.commit()
    print(f"  ✓ Category created with ID {new_id}.")


def delete_category(conn):
    list_categories(conn)
    cat_id = input_int("  Category ID to delete (CASCADE removes its tasks): ", 1)
    with conn.cursor() as cur:
        cur.execute("DELETE FROM categories WHERE id = %s RETURNING name", (cat_id,))
        row = cur.fetchone()
    if row:
        conn.commit()
        print(f"  ✓ Category '{row[0]}' and all its tasks deleted.")
    else:
        conn.rollback()
        print("  Category not found.")


# ── Task Operations ───────────────────────────────────────────

def list_tasks(conn, filter_status=None):
    query = """
        SELECT t.id, t.title, t.status, t.priority, t.due_date, c.name
        FROM tasks t
        INNER JOIN categories c ON t.category_id = c.id
        {where}
        ORDER BY t.priority, t.due_date
    """
    params = ()
    if filter_status:
        query = query.format(where="WHERE t.status = %s")
        params = (filter_status,)
    else:
        query = query.format(where="")

    with conn.cursor() as cur:
        cur.execute(query, params)
        rows = cur.fetchall()

    # Replace priority number with label
    rows = [(r[0], r[1], r[2], PRIORITY_LABEL[r[3]], r[4], r[5]) for r in rows]
    print_table(rows, ["ID", "Title", "Status", "Priority", "Due Date", "Category"])


def add_task(conn):
    list_categories(conn)
    cat_id   = input_int("  Category ID: ", 1)
    title    = input("  Task title: ").strip()
    desc     = input("  Description (optional): ").strip() or None
    status   = input_choice("  Status [pending/in_progress/done]: ", STATUS_OPTIONS)
    priority = input_int("  Priority [1=High, 2=Medium, 3=Low]: ", 1, 3)
    due_date = input("  Due date (YYYY-MM-DD, optional): ").strip() or None

    with conn.cursor() as cur:
        cur.execute(
            """INSERT INTO tasks (title, description, status, priority, due_date, category_id)
               VALUES (%s, %s, %s, %s, %s, %s) RETURNING id""",
            (title, desc, status, priority, due_date, cat_id)
        )
        new_id = cur.fetchone()[0]
    conn.commit()
    print(f"  ✓ Task created with ID {new_id}.")


def update_task(conn):
    list_tasks(conn)
    task_id = input_int("  Task ID to update: ", 1)

    with conn.cursor() as cur:
        cur.execute("SELECT title, status, priority, due_date FROM tasks WHERE id = %s", (task_id,))
        row = cur.fetchone()

    if not row:
        print("  Task not found.")
        return

    print(f"  Current → title: {row[0]} | status: {row[1]} | priority: {PRIORITY_LABEL[row[2]]} | due: {row[3]}")
    new_status   = input_choice(f"  New status [{'/'.join(STATUS_OPTIONS)}]: ", STATUS_OPTIONS)
    new_priority = input_int("  New priority [1=High, 2=Medium, 3=Low]: ", 1, 3)
    new_due      = input("  New due date (YYYY-MM-DD, leave blank to keep): ").strip() or row[3]

    with conn.cursor() as cur:
        cur.execute(
            "UPDATE tasks SET status=%s, priority=%s, due_date=%s WHERE id=%s",
            (new_status, new_priority, new_due, task_id)
        )
    conn.commit()
    print("  ✓ Task updated.")


def delete_task(conn):
    list_tasks(conn)
    task_id = input_int("  Task ID to delete: ", 1)
    with conn.cursor() as cur:
        cur.execute("DELETE FROM tasks WHERE id = %s RETURNING title", (task_id,))
        row = cur.fetchone()
    if row:
        conn.commit()
        print(f"  ✓ Task '{row[0]}' deleted.")
    else:
        conn.rollback()
        print("  Task not found.")


def summary_report(conn):
    with conn.cursor() as cur:
        cur.execute("""
            SELECT c.name,
                   COUNT(t.id)                                              AS total,
                   SUM(CASE WHEN t.status = 'done'        THEN 1 ELSE 0 END) AS done,
                   SUM(CASE WHEN t.status = 'in_progress' THEN 1 ELSE 0 END) AS in_progress,
                   SUM(CASE WHEN t.status = 'pending'     THEN 1 ELSE 0 END) AS pending
            FROM categories c
            LEFT JOIN tasks t ON c.id = t.category_id
            GROUP BY c.name
            ORDER BY total DESC
        """)
        rows = cur.fetchall()
    print_table(rows, ["Category", "Total", "Done", "In Progress", "Pending"])


# ── Main Menu ─────────────────────────────────────────────────

MENU = """
╔══════════════════════════════════════╗
║   Task & Category Management System  ║
╠══════════════════════════════════════╣
║  CATEGORIES                          ║
║   1. List categories                 ║
║   2. Add category                    ║
║   3. Delete category                 ║
╠══════════════════════════════════════╣
║  TASKS                               ║
║   4. List all tasks                  ║
║   5. List tasks by status            ║
║   6. Add task                        ║
║   7. Update task                     ║
║   8. Delete task                     ║
╠══════════════════════════════════════╣
║  REPORTS                             ║
║   9. Summary report                  ║
╠══════════════════════════════════════╣
║   0. Exit                            ║
╚══════════════════════════════════════╝
"""

def main():
    try:
        conn = get_connection()
        print("  ✓ Connected to PostgreSQL database.")
    except Exception as e:
        print(f"  ✗ Connection failed: {e}")
        return

    actions = {
        "1": lambda: list_categories(conn),
        "2": lambda: add_category(conn),
        "3": lambda: delete_category(conn),
        "4": lambda: list_tasks(conn),
        "5": lambda: list_tasks(conn, input_choice("  Filter by status [pending/in_progress/done]: ", STATUS_OPTIONS)),
        "6": lambda: add_task(conn),
        "7": lambda: update_task(conn),
        "8": lambda: delete_task(conn),
        "9": lambda: summary_report(conn),
    }

    while True:
        print(MENU)
        choice = input("  Select an option: ").strip()
        if choice == "0":
            print("  Goodbye!")
            break
        elif choice in actions:
            try:
                actions[choice]()
            except psycopg2.errors.UniqueViolation:
                conn.rollback()
                print("  ✗ Error: A record with that name already exists (UNIQUE constraint).")
            except psycopg2.errors.ForeignKeyViolation:
                conn.rollback()
                print("  ✗ Error: Referenced category does not exist (FK constraint).")
            except psycopg2.errors.CheckViolation:
                conn.rollback()
                print("  ✗ Error: Value violates a CHECK constraint.")
            except Exception as e:
                conn.rollback()
                print(f"  ✗ Unexpected error: {e}")
        else:
            print("  Invalid option.")

    conn.close()


if __name__ == "__main__":
    main()
