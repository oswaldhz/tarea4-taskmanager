const express = require("express");
const session = require("express-session");
const bodyParser = require("body-parser");
const bcrypt = require("bcryptjs");
const db = require("./db");

const app = express();
app.set("view engine", "ejs");
app.use(bodyParser.urlencoded({ extended: true }));
app.use(express.static("public"));
app.use(
  session({ secret: "tarea4secret", resave: false, saveUninitialized: false }),
);

function requireLogin(req, res, next) {
  if (!req.session.userId) return res.redirect("/login");
  next();
}

// ---------- LOGIN ----------
app.get("/login", (req, res) => res.render("login", { error: null }));

app.post("/login", (req, res) => {
  const { username, password } = req.body;
  db.get("SELECT * FROM users WHERE username = ?", [username], (err, user) => {
    if (!user || !bcrypt.compareSync(password, user.password)) {
      return res.render("login", { error: "Usuario o contraseña incorrectos" });
    }
    req.session.userId = user.id;
    res.redirect("/tasks");
  });
});

app.get("/logout", (req, res) => {
  req.session.destroy(() => res.redirect("/login"));
});

// ---------- CRUD DE TAREAS ----------
app.get("/tasks", requireLogin, (req, res) => {
  db.all(
    "SELECT * FROM tasks WHERE user_id = ?",
    [req.session.userId],
    (err, tasks) => {
      res.render("tasks", { tasks });
    },
  );
});

app.post("/tasks/create", requireLogin, (req, res) => {
  const { title, description } = req.body;
  if (!title || title.trim() === "" || title.length > 100) {
    return res.redirect("/tasks?error=titulo_invalido");
  }
  db.run(
    "INSERT INTO tasks (title, description, user_id) VALUES (?, ?, ?)",
    [title, description, req.session.userId],
    () => res.redirect("/tasks"),
  );
});

app.post("/tasks/update/:id", requireLogin, (req, res) => {
  const { title, description, status } = req.body;
  db.run(
    "UPDATE tasks SET title=?, description=?, status=? WHERE id=? AND user_id=?",
    [title, description, status, req.params.id, req.session.userId],
    () => res.redirect("/tasks"),
  );
});

app.post("/tasks/delete/:id", requireLogin, (req, res) => {
  db.run(
    "DELETE FROM tasks WHERE id=? AND user_id=?",
    [req.params.id, req.session.userId],
    () => res.redirect("/tasks"),
  );
});

app.listen(3000, () => console.log("Servidor en http://localhost:3000"));
