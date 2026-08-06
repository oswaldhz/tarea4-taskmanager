import time

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class TasksPage:
    URL = "http://localhost:3000/tasks"

    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)

    def create_task(self, title, description=""):
        # Typing can race with an in-flight navigation (e.g. right after the
        # login redirect) and get dropped, so retry until the field actually
        # holds the title.
        self.driver.find_element(By.ID, "new-title").clear()
        self.driver.find_element(By.ID, "new-title").send_keys(title)
        self.wait.until(
            lambda d: d.find_element(By.ID, "new-title").get_attribute("value")
            == title
        )
        self.driver.find_element(By.ID, "new-description").send_keys(description)
        # The submit triggers a full page reload: the title input comes back
        # empty. If the click was lost during navigation, retry it.
        deadline = time.time() + 15
        while time.time() < deadline:
            try:
                self.driver.find_element(By.ID, "btn-create").click()
            except Exception:
                pass
            time.sleep(0.2)
            if self._new_title_value() == "":
                return
        raise TimeoutError("El formulario de creación no se recargó tras crear la tarea")

    def _new_title_value(self):
        try:
            return self.driver.find_element(By.ID, "new-title").get_attribute("value")
        except Exception:
            return None

    def task_exists(self, title, timeout=5):
        try:
            WebDriverWait(self.driver, timeout).until(
                lambda d: title in d.page_source
            )
            return True
        except Exception:
            return False

    def delete_first_task(self):
        buttons = self.wait.until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".btn-delete"))
        )
        buttons[0].click()
        # Wait for the table to re-render after the redirect
        self.wait.until(EC.presence_of_element_located((By.ID, "tasks-table")))

    def count_tasks(self):
        self.wait.until(EC.presence_of_element_located((By.ID, "tasks-table")))
        return len(self.driver.find_elements(By.CSS_SELECTOR, "#tasks-table tr"))