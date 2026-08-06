from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class TasksPage:
    URL = "http://localhost:3000/tasks"

    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)

    def create_task(self, title, description=""):
        self.driver.find_element(By.ID, "new-title").send_keys(title)
        self.driver.find_element(By.ID, "new-description").send_keys(description)
        self.driver.find_element(By.ID, "btn-create").click()
        # Wait for the page to reload and the create form to be present again
        self.wait.until(EC.presence_of_element_located((By.ID, "new-title")))

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