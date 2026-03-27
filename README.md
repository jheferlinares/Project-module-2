# Task & Category Management System
**CSE 310 – Module 2: SQL Relational Databases**  
Author: Jhefersson Linares

---

## Overview
A command-line application that manages tasks organized by categories using a PostgreSQL relational database. It demonstrates relational schema design, data integrity constraints, and full CRUD operations via SQL.

---

## Relational Schema

```
categories                        tasks
──────────────────────            ──────────────────────────────────
id          SERIAL  PK            id          SERIAL  PK
name        VARCHAR NOT NULL       title       VARCHAR NOT NULL
            UNIQUE                 description TEXT
description TEXT                  status      VARCHAR CHECK (pending|in_progress|done)
created_at  TIMESTAMP             priority    SMALLINT CHECK (1-3)
                                  due_date    DATE
                                  category_id INTEGER FK → categories(id)
                                              ON DELETE CASCADE
                                  created_at  TIMESTAMP
```

**Relationship:** One category → Many tasks (1:N)

---

## Constraints Implemented
| Constraint      | Where Applied                          |
|-----------------|----------------------------------------|
| PRIMARY KEY     | `categories.id`, `tasks.id`            |
| FOREIGN KEY     | `tasks.category_id → categories.id`    |
| ON DELETE CASCADE | Deleting a category removes its tasks |
| NOT NULL        | `categories.name`, `tasks.title`, `tasks.status`, `tasks.priority`, `tasks.category_id` |
| UNIQUE          | `categories.name`                      |
| CHECK           | `tasks.status`, `tasks.priority`       |
| DEFAULT         | `tasks.status = 'pending'`, `tasks.priority = 2` |

---

## Setup

### 1. Install PostgreSQL
Download from https://www.postgresql.org/download/

### 2. Create the database
```sql
CREATE DATABASE taskdb;
```

### 3. Run the SQL scripts
```bash
psql -U postgres -d taskdb -f schema.sql
psql -U postgres -d taskdb -f seed.sql
```

### 4. Configure credentials
Edit `.env` with your PostgreSQL credentials:
```
DB_HOST=localhost
DB_PORT=5432
DB_NAME=taskdb
DB_USER=postgres
DB_PASSWORD=your_password_here
```

### 5. Install Python dependencies
```bash
pip install -r requirements.txt
```

### 6. Run the application
```bash
python app.py
```

---

## Features
- **Categories:** list, add, delete (with cascade)
- **Tasks:** list all, filter by status, add, update, delete
- **Reports:** summary per category (total / done / in_progress / pending)
- **Integrity errors** are caught and displayed with clear messages

---

## SQL Concepts Demonstrated
- DDL: `CREATE TABLE`, `DROP TABLE`, constraints, indexes
- DML: `INSERT`, `SELECT`, `UPDATE`, `DELETE`
- Joins: `INNER JOIN`, `LEFT JOIN`
- Aggregation: `COUNT`, `SUM`, `GROUP BY`
- Subqueries in `UPDATE`/`DELETE`
- Cascade deletes via FK constraint

---

## File Structure
```
Project module 2/
├── schema.sql        ← DDL: table definitions and constraints
├── seed.sql          ← Sample data
├── queries.sql       ← CRUD + JOIN query examples
├── app.py            ← Python CLI application
├── requirements.txt  ← Python dependencies
├── .env              ← Database credentials (not committed)
└── README.md
```
