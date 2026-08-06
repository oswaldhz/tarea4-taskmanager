from selenium.webdriver.support.ui import WebDriverWait
from pages.login_page import LoginPage


def _wait_url(driver, text, timeout=10):
    return WebDriverWait(driver, timeout).until(
        lambda d: text in d.current_url
    )


def test_login_camino_feliz(driver):
    """Historia 1 - login con credenciales correctas redirige a /tasks"""
    page = LoginPage(driver)
    page.open()
    page.login("testuser", "Test1234!")
    assert _wait_url(driver, "/tasks")


def test_login_negativo_credenciales_invalidas(driver):
    """Historia 1 - login con contraseña incorrecta muestra error y no redirige"""
    page = LoginPage(driver)
    page.open()
    page.login("testuser", "clave_incorrecta")
    WebDriverWait(driver, 10).until(
        lambda d: page.get_error_message() is not None
    )
    assert page.get_error_message() == "Usuario o contraseña incorrectos"
    assert "/login" in driver.current_url


def test_login_limite_campos_vacios(driver):
    """Historia 1 - límite: enviar el formulario sin llenar campos no debe loguear"""
    page = LoginPage(driver)
    page.open()
    driver.find_element("id", "btn-login").click()
    assert _wait_url(driver, "/login")
