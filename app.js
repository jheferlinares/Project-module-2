/**
 * Task & Category Management System
 * Module 2 - SQL Relational Databases
 * Author: Jhefersson Linares
 */

require("dotenv").config();
const { Pool } = require("pg");
const rl = require("readline-sync");

const pool = new Pool({
  host:     process.env.DB_HOST     || "localhost",
  port:     process.env.DB_PORT     || 5432,
  database: process.env.DB_NAME     || "taskdb",
  user:     process.env.DB_USER     || "postgres",
  password: process.env.DB_PASSWORD || "",
});

const PRIORITY_LABEL = { 1: "High", 2: "Medium", 3: "Low" };
const STATUS_OPTIONS  = ["pending", "in_progress", "done"];

// ── Helpers ──────────────────────────────────────────────────

function printTable(rows, headers) {
  if (!rows.length) { console.log("  (no records found)"); return; }
  const widths = headers.map((h, i) =>
    Math.max(h.length, ...rows.map(r => String(r[i] ?? "").length))
  );
  const fmt = row => "  " + row.map((v, i) => String(v ?? "").padEnd(widths[i])).join("  ");
  console.log(fmt(headers));
  console.log("  " + widths.map(w => "-".repeat(w)).join("  "));
  rows.forEach(r => console.log(fmt(r)));
}

function inputChoice(prompt, options) {
  while (true) {
    const val = rl.question(`  ${prompt} `).trim().toLowerCase();
    if (options.includes(val)) return val;
    console.log(`  Invalid. Choose from: ${options.join(", ")}`);
  }
}

function inputInt(prompt, min, max) {
  while (true) {
    const val = parseInt(rl.question(`  ${prompt} `).trim(), 10);
    if (!isNaN(val) && val >= min && val <= max) return val;
    console.log(`  Enter a number between ${min} and ${max}.`);
  }
}

async function query(sql, params = []) {
  const res = await pool.query(sql, params);
  return res.rows;
}

// ── Categories ────────────────────────────────────────────────

async function listCategories() {
  const rows = await query(`
    SELECT c.id, c.name, c.description, COUNT(t.id) AS tasks
    FROM categories c
    LEFT JOIN tasks t ON c.id = t.category_id
    GROUP BY c.id ORDER BY c.name
  `);
  printTable(rows.map(r => [r.id, r.name, r.description ?? "", r.tasks]),
    ["ID", "Name", "Description", "Tasks"]);
}

async function addCategory() {
  const name = rl.question("  Category name: ").trim();
  const desc = rl.question("  Description (optional): ").trim() || null;
  const res  = await query(
    "INSERT INTO categories (name, description) VALUES ($1, $2) RETURNING id",
    [name, desc]
  );
  console.log(`  ✓ Category created with ID ${res[0].id}.`);
}

async function deleteCategory() {
  await listCategories();
  const id  = inputInt("Category ID to delete (CASCADE removes its tasks):", 1, 99999);
  const res = await query("DELETE FROM categories WHERE id = $1 RETURNING name", [id]);
  if (res.length) console.log(`  ✓ Category '${res[0].name}' and all its tasks deleted.`);
  else            console.log("  Category not found.");
}

// ── Tasks ─────────────────────────────────────────────────────

async function listTasks(filterStatus = null) {
  const where  = filterStatus ? "WHERE t.status = $1" : "";
  const params = filterStatus ? [filterStatus] : [];
  const rows   = await query(`
    SELECT t.id, t.title, t.status, t.priority, t.due_date, c.name
    FROM tasks t
    INNER JOIN categories c ON t.category_id = c.id
    ${where}
    ORDER BY t.priority, t.due_date
  `, params);
  printTable(
    rows.map(r => [r.id, r.title, r.status, PRIORITY_LABEL[r.priority], r.due_date?.toISOString().split("T")[0] ?? "", r.name]),
    ["ID", "Title", "Status", "Priority", "Due Date", "Category"]
  );
}

async function addTask() {
  await listCategories();
  const catId    = inputInt("Category ID:", 1, 99999);
  const title    = rl.question("  Task title: ").trim();
  const desc     = rl.question("  Description (optional): ").trim() || null;
  const status   = inputChoice("Status [pending/in_progress/done]:", STATUS_OPTIONS);
  const priority = inputInt("Priority [1=High, 2=Medium, 3=Low]:", 1, 3);
  const due      = rl.question("  Due date (YYYY-MM-DD, optional): ").trim() || null;
  const res      = await query(
    `INSERT INTO tasks (title, description, status, priority, due_date, category_id)
     VALUES ($1,$2,$3,$4,$5,$6) RETURNING id`,
    [title, desc, status, priority, due, catId]
  );
  console.log(`  ✓ Task created with ID ${res[0].id}.`);
}

async function updateTask() {
  await listTasks();
  const id  = inputInt("Task ID to update:", 1, 99999);
  const cur = await query("SELECT title, status, priority, due_date FROM tasks WHERE id = $1", [id]);
  if (!cur.length) { console.log("  Task not found."); return; }
  const t = cur[0];
  console.log(`  Current → title: ${t.title} | status: ${t.status} | priority: ${PRIORITY_LABEL[t.priority]} | due: ${t.due_date?.toISOString().split("T")[0] ?? ""}`);
  const newStatus   = inputChoice(`New status [${STATUS_OPTIONS.join("/")}]:`, STATUS_OPTIONS);
  const newPriority = inputInt("New priority [1=High, 2=Medium, 3=Low]:", 1, 3);
  const newDue      = rl.question("  New due date (YYYY-MM-DD, leave blank to keep): ").trim()
                      || t.due_date?.toISOString().split("T")[0] || null;
  await query("UPDATE tasks SET status=$1, priority=$2, due_date=$3 WHERE id=$4",
    [newStatus, newPriority, newDue, id]);
  console.log("  ✓ Task updated.");
}

async function deleteTask() {
  await listTasks();
  const id  = inputInt("Task ID to delete:", 1, 99999);
  const res = await query("DELETE FROM tasks WHERE id = $1 RETURNING title", [id]);
  if (res.length) console.log(`  ✓ Task '${res[0].title}' deleted.`);
  else            console.log("  Task not found.");
}

async function summaryReport() {
  const rows = await query(`
    SELECT c.name,
           COUNT(t.id) AS total,
           SUM(CASE WHEN t.status='done'        THEN 1 ELSE 0 END) AS done,
           SUM(CASE WHEN t.status='in_progress' THEN 1 ELSE 0 END) AS in_progress,
           SUM(CASE WHEN t.status='pending'     THEN 1 ELSE 0 END) AS pending
    FROM categories c
    LEFT JOIN tasks t ON c.id = t.category_id
    GROUP BY c.name ORDER BY total DESC
  `);
  printTable(
    rows.map(r => [r.name, r.total, r.done, r.in_progress, r.pending]),
    ["Category", "Total", "Done", "In Progress", "Pending"]
  );
}

// ── Main Menu ─────────────────────────────────────────────────

const MENU = `
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
╚══════════════════════════════════════╝`;

async function main() {
  try {
    await pool.query("SELECT 1");
    console.log("  ✓ Connected to PostgreSQL database.");
  } catch (e) {
    console.error(`  ✗ Connection failed: ${e.message}`);
    process.exit(1);
  }

  const actions = {
    "1": () => listCategories(),
    "2": () => addCategory(),
    "3": () => deleteCategory(),
    "4": () => listTasks(),
    "5": () => listTasks(inputChoice("Filter by status [pending/in_progress/done]:", STATUS_OPTIONS)),
    "6": () => addTask(),
    "7": () => updateTask(),
    "8": () => deleteTask(),
    "9": () => summaryReport(),
  };

  while (true) {
    console.log(MENU);
    const choice = rl.question("  Select an option: ").trim();
    if (choice === "0") { console.log("  Goodbye!"); break; }
    if (!actions[choice]) { console.log("  Invalid option."); continue; }
    try {
      await actions[choice]();
    } catch (e) {
      if (e.code === "23505") console.log("  ✗ Error: A record with that name already exists (UNIQUE constraint).");
      else if (e.code === "23503") console.log("  ✗ Error: Referenced category does not exist (FK constraint).");
      else if (e.code === "23514") console.log("  ✗ Error: Value violates a CHECK constraint.");
      else console.log(`  ✗ Unexpected error: ${e.message}`);
    }
  }

  await pool.end();
}

main();
