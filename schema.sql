-- ============================================================
-- Task & Category Management System
-- Module 2 - SQL Relational Databases
-- Author: Jhefersson Linares
-- ============================================================

-- Drop tables if they exist (order matters due to FK)
DROP TABLE IF EXISTS tasks;
DROP TABLE IF EXISTS categories;

-- ============================================================
-- TABLE: categories
-- Parent table in the One-to-Many relationship
-- ============================================================
CREATE TABLE categories (
    id          SERIAL PRIMARY KEY,
    name        VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- TABLE: tasks
-- Child table referencing categories (FK)
-- ON DELETE CASCADE: deleting a category removes its tasks
-- ============================================================
CREATE TABLE tasks (
    id          SERIAL PRIMARY KEY,
    title       VARCHAR(200) NOT NULL,
    description TEXT,
    status      VARCHAR(20)  NOT NULL DEFAULT 'pending'
                             CHECK (status IN ('pending', 'in_progress', 'done')),
    priority    SMALLINT     NOT NULL DEFAULT 2
                             CHECK (priority BETWEEN 1 AND 3),  -- 1=High, 2=Medium, 3=Low
    due_date    DATE,
    category_id INTEGER      NOT NULL,
    created_at  TIMESTAMP    DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_category
        FOREIGN KEY (category_id)
        REFERENCES categories(id)
        ON DELETE CASCADE
);

-- Index to speed up queries filtering by category
CREATE INDEX idx_tasks_category ON tasks(category_id);
CREATE INDEX idx_tasks_status   ON tasks(status);
