-- ============================================================
-- Seed Data
-- ============================================================

INSERT INTO categories (name, description) VALUES
    ('Work',     'Professional and job-related tasks'),
    ('Personal', 'Personal errands and goals'),
    ('Study',    'Academic and learning activities'),
    ('Health',   'Fitness, diet, and medical tasks');

INSERT INTO tasks (title, description, status, priority, due_date, category_id) VALUES
    ('Prepare project report',   'Write the final report for Module 2',  'in_progress', 1, '2026-03-25', 1),
    ('Team meeting',             'Weekly sync with the dev team',         'pending',     2, '2026-03-20', 1),
    ('Buy groceries',            'Milk, eggs, bread, vegetables',         'pending',     3, '2026-03-19', 2),
    ('Call the dentist',         'Schedule a cleaning appointment',       'pending',     2, '2026-03-22', 4),
    ('Read PostgreSQL docs',     'Study chapters 5-8 on indexing',        'in_progress', 1, '2026-03-21', 3),
    ('Practice SQL JOINs',       'Complete exercises on Inner/Left JOIN', 'pending',     1, '2026-03-20', 3),
    ('Morning run',              '5 km run in the park',                  'done',        2, '2026-03-18', 4),
    ('Update LinkedIn profile',  'Add new skills and recent projects',    'pending',     3, '2026-03-28', 1),
    ('Watch SQL tutorial video', 'YouTube series on advanced queries',    'done',        2, '2026-03-17', 3),
    ('Meal prep for the week',   'Cook and portion meals for 5 days',     'pending',     2, '2026-03-22', 2);
