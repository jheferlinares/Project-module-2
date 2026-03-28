# Overview

As a software engineer focused on backend development, I wanted to deepen my understanding of relational databases by building a real application that interacts with a SQL database. This project allowed me to explore how data relationships, constraints, and queries work in practice — not just in theory.

I built a Task and Category Management System that connects to a PostgreSQL database and allows users to manage tasks organized by categories through a command-line interface. The application performs full CRUD operations (Create, Read, Update, Delete), executes JOIN queries across two related tables, uses aggregate functions for reporting, and filters tasks by date range — all driven by user input at runtime.

To use the program, run `node app.js` in the terminal. A menu will appear with numbered options to list categories, add or delete tasks, filter by status or date range, and view a summary report. All data is persisted in the PostgreSQL database.

My purpose for writing this software was to gain hands-on experience with relational database design, SQL constraints, and how a backend application communicates with a database using parameterized queries to prevent SQL injection.

[Software Demo Video](https://youtu.be/PqLdwW8AS60)

# Relational Database

I used **PostgreSQL** as the relational database management system.

The database is named `taskdb` and contains two related tables:

**categories** — stores task categories
| Column      | Type         | Constraints                  |
|-------------|--------------|------------------------------|
| id          | SERIAL       | PRIMARY KEY                  |
| name        | VARCHAR(100) | NOT NULL, UNIQUE             |
| description | TEXT         |                              |
| created_at  | TIMESTAMP    | DEFAULT CURRENT_TIMESTAMP    |

**tasks** — stores individual tasks linked to a category
| Column      | Type         | Constraints                                      |
|-------------|--------------|--------------------------------------------------|
| id          | SERIAL       | PRIMARY KEY                                      |
| title       | VARCHAR(200) | NOT NULL                                         |
| description | TEXT         |                                                  |
| status      | VARCHAR(20)  | NOT NULL, CHECK (pending, in_progress, done)     |
| priority    | SMALLINT     | NOT NULL, CHECK (1–3), DEFAULT 2                 |
| due_date    | DATE         |                                                  |
| category_id | INTEGER      | NOT NULL, FOREIGN KEY → categories(id) ON DELETE CASCADE |
| created_at  | TIMESTAMP    | DEFAULT CURRENT_TIMESTAMP                        |

The relationship is **One-to-Many**: one category can have many tasks. Deleting a category automatically removes all its tasks via the `ON DELETE CASCADE` constraint.

# Development Environment

- **pgAdmin 4** — GUI tool used to create the database and run SQL scripts
- **Visual Studio Code** — code editor
- **Node.js v22** — JavaScript runtime environment
- **npm** — package manager

**Programming Language:** JavaScript (Node.js)

**Libraries:**
- `pg` (node-postgres) — connects Node.js to PostgreSQL and executes queries
- `dotenv` — loads database credentials from the `.env` file
- `readline-sync` — handles synchronous user input in the terminal

# Useful Websites

- [PostgreSQL Official Documentation](https://www.postgresql.org/docs/)
- [node-postgres (pg) Documentation](https://node-postgres.com/)
- [W3Schools SQL Tutorial](https://www.w3schools.com/sql/)
- [dotenv npm package](https://www.npmjs.com/package/dotenv)
- [readline-sync npm package](https://www.npmjs.com/package/readline-sync)

# Future Work

- Add a web-based interface using Express.js so the app can run in a browser
- Implement user authentication so each user manages their own tasks
- Add support for task tags and filtering by multiple criteria at once
