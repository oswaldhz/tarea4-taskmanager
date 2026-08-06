import pytest
import os
import time
import base64
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import SessionNotCreatedException
from webdriver_manager.chrome import ChromeDriverManager
import pytest_html

SCREENSHOT_DIR = os.path.join(os.path.dirname(__file__), "screenshots")
os.makedirs(SCREENSHOT_DIR, exist_ok=True)


@pytest.fixture(scope="session", autouse=True)
def reset_database():
    """Runs once before the whole test session starts, and once again
    after all tests finish. Individual tests are NOT reset between each
    other, since the update/delete tests already create their own task
    before acting on it."""
    requests.post("http://localhost:3000/test/reset")
    yield
    requests.post("http://localhost:3000/test/reset")


@pytest.fixture
def driver():
    options = webdriver.ChromeOptions()
    # options.add_argument("--headless")  # uncomment to run without opening a window
    service = Service(ChromeDriverManager().install())

    # Chrome can fail to start with "session not created" under memory
    # pressure or right after an update. Retry the launch a few times.
    attempt = 0
    while True:
        try:
            drv = webdriver.Chrome(service=service, options=options)
            break
        except SessionNotCreatedException:
            attempt += 1
            if attempt >= 3:
                raise
            time.sleep(3)

    drv.implicitly_wait(5)
    drv.maximize_window()
    yield drv
    drv.quit()


def _capture_screenshot(driver):
    """Captures the ENTIRE page, not just the visible viewport or a
    single element. First waits for the page to finish loading and
    gives the renderer a moment to settle, then resizes the window to
    the full document dimensions so no part of the page gets cut off.
    Falls back to a plain viewport screenshot if anything fails."""
    try:
        WebDriverWait(driver, 10).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )
    except Exception:
        pass
    time.sleep(1)

    try:
        height = driver.execute_script(
            "return Math.max(document.body.scrollHeight, "
            "document.documentElement.scrollHeight)"
        )
        width = driver.execute_script(
            "return Math.max(document.body.scrollWidth, "
            "document.documentElement.scrollWidth)"
        )
        driver.set_window_size(max(width, 1280), max(height, 720))
        return driver.get_screenshot_as_png()
    except Exception:
        return driver.get_screenshot_as_png()


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    extra = getattr(report, "extra", [])

    if report.when == "call":
        driver = item.funcargs.get("driver")
        if driver is not None:
            filename = f"{item.name}_{'PASS' if report.passed else 'FAIL'}.png"
            path = os.path.join(SCREENSHOT_DIR, filename)

            png_bytes = _capture_screenshot(driver)
            with open(path, "wb") as f:
                f.write(png_bytes)

            # Embed the same full-page screenshot directly into report.html
            screenshot_b64 = base64.b64encode(png_bytes).decode("utf-8")
            extra.append(pytest_html.extras.image(screenshot_b64, name=filename))

    report.extra = extra