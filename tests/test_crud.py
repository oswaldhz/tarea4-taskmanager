import time
from pages.login_page import LoginPage
from pages.tasks_page import TasksPage

def login_helper(driver):
    login = LoginPage(driver)
    login.open()
    login.login("testuser", "Test1234!")

# ---------- Historia 2: Crear (Create) ----------
def test_crear_tarea_camino_feliz(driver):
    login_helper(driver)
    tasks = TasksPage(driver)
    tasks.create_task("Estudiar Selenium", "Repasar Page Objects")
    assert tasks.task_exists("Estudiar Selenium")

def test_crear_tarea_negativo_titulo_vacio(driver):
    login_helper(driver)
    tasks = TasksPage(driver)
    antes = tasks.count_tasks()
    tasks.create_task("", "sin titulo")
    despues = TasksPage(driver).count_tasks()
    assert despues == antes  # no debe crear la fila

def test_crear_tarea_limite_100_caracteres(driver):
    login_helper(driver)
    tasks = TasksPage(driver)
    titulo_limite = "A" * 100
    tasks.create_task(titulo_limite, "prueba de límite")
    assert tasks.task_exists(titulo_limite)

# ---------- Historia 3: Listar (Read) ----------
def test_listar_tareas_camino_feliz(driver):
    login_helper(driver)
    driver.get("http://localhost:3000/tasks")
    assert "Gestor de Tareas" in driver.page_source

def test_listar_sin_sesion_redirige_login(driver):
    driver.get("http://localhost:3000/tasks")
    assert "/login" in driver.current_url

# ---------- Historia 4: Actualizar (Update) ----------
def test_actualizar_tarea_camino_feliz(driver):
    login_helper(driver)
    tasks = TasksPage(driver)
    tasks.create_task("Tarea editable", "desc original")
    time.sleep(1)
    campos = driver.find_elements("css selector", "input[name='title']")
    campos[-1].clear()
    campos[-1].send_keys("Tarea editada")
    driver.find_elements("css selector", ".btn-edit")[-1].click()
    assert "Tarea editada" in driver.page_source

# ---------- Historia 5: Eliminar (Delete) ----------
def test_eliminar_tarea_camino_feliz(driver):
    login_helper(driver)
    tasks = TasksPage(driver)
    tasks.create_task("Tarea a borrar", "desc")
    time.sleep(1)
    antes = tasks.count_tasks()
    tasks.delete_first_task()
    time.sleep(1)
    despues = TasksPage(driver).count_tasks()
    assert despues < antes