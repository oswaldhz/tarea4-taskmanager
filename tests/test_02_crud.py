import requests
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


def test_crear_tarea_limite_101_caracteres_rechazada(driver):
    """TS-3 (límite): crear con 101 caracteres es rechazado y no agrega fila"""
    login_helper(driver)
    tasks = TasksPage(driver)
    antes = tasks.count_tasks()
    tasks.create_task("D" * 101, "x")
    despues = TasksPage(driver).count_tasks()
    assert despues == antes  # el servidor rechaza el título > 100 caracteres


# ---------- Historia 3: Listar (Read) ----------
def test_listar_tareas_camino_feliz(driver):
    login_helper(driver)
    driver.get("http://localhost:3000/tasks")
    assert "Gestor de Tareas" in driver.page_source


def test_listar_sin_sesion_redirige_login(driver):
    driver.get("http://localhost:3000/tasks")
    assert "/login" in driver.current_url


def test_listar_tareas_limite_muchas_tareas(driver):
    """TS-4 (límite): listar 25 tareas muestra todas las filas del listado"""
    requests.post("http://localhost:3000/test/reset")
    login_helper(driver)
    tasks = TasksPage(driver)
    for i in range(25):
        tasks.create_task(f"Tarea limite {i}", "x")
    driver.get("http://localhost:3000/tasks")
    assert tasks.count_tasks() == 25
    assert "Tarea limite 0" in driver.page_source
    assert "Tarea limite 24" in driver.page_source


# ---------- Historia 4: Actualizar (Update) ----------
def test_actualizar_tarea_camino_feliz(driver):
    login_helper(driver)
    tasks = TasksPage(driver)
    tasks.create_task("Tarea editable", "desc original")
    campos = driver.find_elements("css selector", "input[name='title']")
    campos[-1].clear()
    campos[-1].send_keys("Tarea editada")
    driver.find_elements("css selector", ".btn-edit")[-1].click()
    tasks.wait.until(lambda d: "Tarea editada" in d.page_source)
    assert "Tarea editada" in driver.page_source


def test_actualizar_tarea_negativo_titulo_vacio(driver):
    """TS-5 (negativo): actualizar con título vacío conserva el valor anterior"""
    login_helper(driver)
    tasks = TasksPage(driver)
    tasks.create_task("Titulo original", "desc")
    campos = driver.find_elements("css selector", "input[name='title']")
    campos[-1].clear()
    campos[-1].send_keys("")
    driver.find_elements("css selector", ".btn-edit")[-1].click()
    tasks.wait.until(lambda d: "Titulo original" in d.page_source)
    assert "Titulo original" in driver.page_source  # no debe dejar el título en blanco


def test_actualizar_tarea_limite_100_caracteres(driver):
    """TS-5 (límite): actualizar con título de 100 caracteres es aceptado"""
    login_helper(driver)
    tasks = TasksPage(driver)
    tasks.create_task("Tarea", "desc")
    titulo_limite = "B" * 100
    campos = driver.find_elements("css selector", "input[name='title']")
    campos[-1].clear()
    campos[-1].send_keys(titulo_limite)
    driver.find_elements("css selector", ".btn-edit")[-1].click()
    tasks.wait.until(lambda d: titulo_limite in d.page_source)
    assert tasks.task_exists(titulo_limite)


def test_actualizar_tarea_limite_101_caracteres_rechazada(driver):
    """TS-5 (límite): actualizar con 101 caracteres es rechazado y se conserva el título"""
    login_helper(driver)
    tasks = TasksPage(driver)
    tasks.create_task("Titulo valido", "desc")
    campos = driver.find_elements("css selector", "input[name='title']")
    campos[-1].clear()
    campos[-1].send_keys("C" * 101)
    driver.find_elements("css selector", ".btn-edit")[-1].click()
    tasks.wait.until(lambda d: "Titulo valido" in d.page_source)
    assert "Titulo valido" in driver.page_source


# ---------- Historia 5: Eliminar (Delete) ----------
def test_eliminar_tarea_camino_feliz(driver):
    login_helper(driver)
    tasks = TasksPage(driver)
    tasks.create_task("Tarea a borrar", "desc")
    antes = tasks.count_tasks()
    tasks.delete_first_task()
    despues = TasksPage(driver).count_tasks()
    assert despues < antes


def test_eliminar_tarea_negativo_id_manipulado(driver):
    """TS-6 (negativo): eliminar una tarea inexistente (URL manipulada) no borra nada"""
    login_helper(driver)
    tasks = TasksPage(driver)
    tasks.create_task("Tarea segura", "desc")
    antes = tasks.count_tasks()
    driver.execute_async_script(
        "var done = arguments[0];"
        "fetch('/tasks/delete/999999', {method: 'POST'}).then(() => done());"
    )
    tasks.wait.until(lambda d: "Tarea segura" in d.page_source)
    despues = TasksPage(driver).count_tasks()
    assert despues == antes


def test_eliminar_tarea_limite_ultima_tarea(driver):
    """TS-6 (límite): eliminar la última tarea deja el listado vacío"""
    requests.post("http://localhost:3000/test/reset")
    login_helper(driver)
    tasks = TasksPage(driver)
    tasks.create_task("Ultima tarea", "desc")
    tasks.delete_first_task()
    tasks.wait.until(lambda d: "Todavía no tienes tareas" in d.page_source)
    assert "task-row-" not in driver.page_source