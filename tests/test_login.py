from pages.login_page import LoginPage

def test_login_camino_feliz(driver):
    """Historia 1 - login con credenciales correctas redirige a /tasks"""
    page = LoginPage(driver)
    page.open()
    page.login("testuser", "Test1234!")
    assert "/tasks" in driver.current_url

def test_login_negativo_credenciales_invalidas(driver):
    """Historia 1 - login con contraseña incorrecta muestra error y no redirige"""
    page = LoginPage(driver)
    page.open()
    page.login("testuser", "clave_incorrecta")
    assert page.get_error_message() == "Usuario o contraseña incorrectos"
    assert "/login" in driver.current_url

def test_login_limite_campos_vacios(driver):
    """Historia 1 - límite: enviar el formulario sin llenar campos no debe loguear"""
    page = LoginPage(driver)
    page.open()
    driver.find_element("id", "btn-login").click()
    assert "/login" in driver.current_url