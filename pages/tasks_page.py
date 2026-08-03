from selenium.webdriver.common.by import By

class TasksPage:
    URL = "http://localhost:3000/tasks"

    def __init__(self, driver):
        self.driver = driver

    def create_task(self, title, description=""):
        self.driver.find_element(By.ID, "new-title").send_keys(title)
        self.driver.find_element(By.ID, "new-description").send_keys(description)
        self.driver.find_element(By.ID, "btn-create").click()

    def task_exists(self, title):
        return title in self.driver.page_source

    def delete_first_task(self):
        self.driver.find_element(By.CSS_SELECTOR, ".btn-delete").click()

    def count_tasks(self):
        return len(self.driver.find_elements(By.CSS_SELECTOR, "#tasks-table tr"))