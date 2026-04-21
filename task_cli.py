import typer
import sqlite3
from pathlib import Path
from datetime import datetime
from typing import Optional

app = typer.Typer(help="🚀 Elite CLI Task Manager")
DB_FILE = Path("tasks.db")

# ---------------------- DATABASE ----------------------

def get_conn():
    return sqlite3.connect(DB_FILE)


def init_db():
    conn = get_conn()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        task TEXT NOT NULL,
        created_at TEXT,
        completed INTEGER DEFAULT 0
    )
    """)

    conn.commit()
    conn.close()


# ---------------------- CORE DB FUNCTION ----------------------

def execute(query, params=(), fetch=False):
    conn = get_conn()
    cursor = conn.cursor()

    cursor.execute(query, params)
    data = cursor.fetchall() if fetch else None

    conn.commit()
    conn.close()
    return data


# ---------------------- COMMANDS ----------------------

@app.command()
def add(task: str):
    """Add a new task"""
    execute(
        "INSERT INTO tasks (task, created_at) VALUES (?, ?)",
        (task, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    )
    typer.echo(f"✅ Added: {task}")


@app.command()
def list(
    all: bool = typer.Option(False, "--all", help="Show all tasks"),
    completed: bool = typer.Option(False, "--completed", help="Show completed tasks")
):
    """List tasks with filters"""

    if all:
        query = "SELECT * FROM tasks"
    elif completed:
        query = "SELECT * FROM tasks WHERE completed=1"
    else:
        query = "SELECT * FROM tasks WHERE completed=0"

    tasks = execute(query, fetch=True)

    if not tasks:
        typer.echo("No tasks found.")
        return

    for t in tasks:
        status = "✔" if t[3] else "✘"
        typer.echo(f"[{status}] {t[0]} | {t[1]} | {t[2]}")


@app.command()
def complete(task_id: int):
    """Mark task complete"""
    execute("UPDATE tasks SET completed=1 WHERE id=?", (task_id,))
    typer.echo(f"🎉 Completed task {task_id}")


@app.command()
def delete(task_id: int):
    """Delete task"""
    execute("DELETE FROM tasks WHERE id=?", (task_id,))
    typer.echo(f"🗑 Deleted task {task_id}")


@app.command()
def search(keyword: str):
    """Search tasks"""
    tasks = execute(
        "SELECT * FROM tasks WHERE task LIKE ?",
        (f"%{keyword}%",),
        fetch=True
    )

    if not tasks:
        typer.echo("No results.")
        return

    for t in tasks:
        typer.echo(f"[{t[0]}] {t[1]}")


@app.command()
def stats():
    """Show analytics"""
    total = execute("SELECT COUNT(*) FROM tasks", fetch=True)[0][0]
    completed = execute("SELECT COUNT(*) FROM tasks WHERE completed=1", fetch=True)[0][0]

    pending = total - completed

    typer.echo("📊 TASK STATS")
    typer.echo(f"Total     : {total}")
    typer.echo(f"Completed : {completed}")
    typer.echo(f"Pending   : {pending}")


# ---------------------- ENTRY ----------------------

if __name__ == "__main__":
    init_db()
    app()

