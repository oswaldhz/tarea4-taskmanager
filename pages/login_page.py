from selenium.webdriver.common.by import By

class LoginPage:
    URL = "http://localhost:3000/login"

    def __init__(self, driver):
        self.driver = driver

    def open(self):
        self.driver.get(self.URL)

    def login(self, username, password):
        self.driver.find_element(By.ID, "username").send_keys(username)
        self.driver.find_element(By.ID, "password").send_keys(password)
        self.driver.find_element(By.ID, "btn-login").click()

    def get_error_message(self):
        try:
            return self.driver.find_element(By.ID, "error-msg").text
        except:
            return None