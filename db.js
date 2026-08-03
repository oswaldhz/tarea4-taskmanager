const sqlite3 = require("sqlite3").verbose();
const db = new sqlite3.Database("./database.db");

db.serialize(() => {
  db.run(`CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
  )`);

  db.run(`CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT,
    status TEXT DEFAULT 'pendiente',
    user_id INTEGER
  )`);

  // Usuario de prueba fijo para que Selenium siempre pueda loguear
  const bcrypt = require("bcryptjs");
  const hashed = bcrypt.hashSync("Test1234!", 8);
  db.run(
    `INSERT OR IGNORE INTO users (id, username, password) VALUES (1, 'testuser', ?)`,
    [hashed],
  );
});

module.exports = db;
