import os
import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

BASE_URL = os.environ.get("BASE_URL", "http://localhost:8000")


@pytest.fixture(scope="function")
def driver():
    options = Options()
    if os.environ.get("HEADLESS", "1") == "1":
        options.add_argument("--headless=new")
    options.add_argument("--window-size=1440,900")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    drv = webdriver.Chrome(options=options)
    drv.implicitly_wait(2)
    yield drv
    drv.quit()


@pytest.fixture(scope="function")
def meyerhof_page(driver):
    driver.get(f"{BASE_URL}/meyerhof_sementara")
    return driver