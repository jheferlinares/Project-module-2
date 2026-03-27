-- ============================================================
-- CRUD Operations & Query Examples
-- Module 2 - SQL Relational Databases
-- ============================================================


-- ============================================================
-- CREATE (INSERT)
-- ============================================================

-- Add a new category
INSERT INTO categories (name, description)
VALUES ('Finance', 'Budgeting and financial planning');

-- Add a new task linked to a category
INSERT INTO tasks (title, description, status, priority, due_date, category_id)
VALUES ('Review monthly budget', 'Check expenses vs income for March', 'pending', 1, '2026-03-31', 5);


-- ============================================================
-- READ (SELECT)
-- ============================================================

-- 1. All categories
SELECT * FROM categories ORDER BY name;

-- 2. All tasks with their category name (INNER JOIN)
SELECT
    t.id,
    t.title,
    t.status,
    t.priority,
    t.due_date,
    c.name AS category
FROM tasks t
INNER JOIN categories c ON t.category_id = c.id
ORDER BY t.priority, t.due_date;

-- 3. Tasks per category with count (GROUP BY + JOIN)
SELECT
    c.name        AS category,
    COUNT(t.id)   AS total_tasks,
    SUM(CASE WHEN t.status = 'done' THEN 1 ELSE 0 END) AS completed
FROM categories c
LEFT JOIN tasks t ON c.id = t.category_id
GROUP BY c.name
ORDER BY total_tasks DESC;

-- 4. High-priority pending tasks (filter)
SELECT t.title, t.due_date, c.name AS category
FROM tasks t
INNER JOIN categories c ON t.category_id = c.id
WHERE t.priority = 1 AND t.status != 'done'
ORDER BY t.due_date;

-- 5. Categories with NO tasks (LEFT JOIN + NULL check)
SELECT c.name
FROM categories c
LEFT JOIN tasks t ON c.id = t.category_id
WHERE t.id IS NULL;


-- ============================================================
-- UPDATE
-- ============================================================

-- Mark a task as done
UPDATE tasks
SET status = 'done'
WHERE title = 'Practice SQL JOINs';

-- Change priority of all 'Work' tasks to High
UPDATE tasks
SET priority = 1
WHERE category_id = (SELECT id FROM categories WHERE name = 'Work');

-- Rename a category
UPDATE categories
SET name = 'Career', description = 'Career development and work tasks'
WHERE name = 'Work';


-- ============================================================
-- DELETE
-- ============================================================

-- Delete a single task
DELETE FROM tasks
WHERE title = 'Update LinkedIn profile';

-- Delete a category → CASCADE removes its tasks automatically
DELETE FROM categories
WHERE name = 'Finance';


-- ============================================================
-- DATA INTEGRITY TESTS
-- ============================================================

-- Test 1: Insert task with non-existent category_id (should FAIL with FK violation)
-- INSERT INTO tasks (title, status, priority, category_id) VALUES ('Ghost task', 'pending', 2, 999);

-- Test 2: Insert category with duplicate name (should FAIL with UNIQUE violation)
-- INSERT INTO categories (name) VALUES ('Study');

-- Test 3: Insert task with invalid status (should FAIL with CHECK violation)
-- INSERT INTO tasks (title, status, priority, category_id) VALUES ('Bad task', 'unknown', 2, 1);

-- Test 4: Insert task without title (should FAIL with NOT NULL violation)
-- INSERT INTO tasks (status, priority, category_id) VALUES ('pending', 2, 1);
