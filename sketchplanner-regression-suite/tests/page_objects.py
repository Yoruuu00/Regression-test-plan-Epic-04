"""
Page Object untuk /meyerhof_sementara.

PENTING: halaman ini dibangun dengan Alpine.js dan TIDAK memiliki atribut
id/name/data-testid pada elemen form-nya — hanya `x-model`. Locator di bawah
memakai XPath relatif ke teks <label>, yang rapuh terhadap perubahan teks atau
struktur HTML. Lihat README.md bagian "Catatan Penting tentang Testability"
untuk rekomendasi perbaikan (tambahkan data-testid).
"""
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class MeyerhofPage:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)

    # --- Locators (relatif ke teks label, lihat catatan di atas) ---
    def _input_after_label(self, label_text):
        xpath = f"//label[normalize-space(text())='{label_text}']/following-sibling::input"
        return self.driver.find_element(By.XPATH, xpath)

    def point_label_input(self):
        return self._input_after_label("Point Label")

    def safety_factor_input(self):
        return self._input_after_label("Safety Factor (SF)")

    def pile_diameter_input(self):
        return self._input_after_label("Pile Diameter (m)")

    def pile_depth_input(self):
        return self._input_after_label("Pile Depth (m)")

    def depth_interval_input(self):
        return self._input_after_label("Depth Interval (m)")

    def required_load_input(self):
        return self._input_after_label("Required Load (kN)")

    def water_content_input(self):
        return self._input_after_label("Water Content (%)")

    def calculate_button(self):
        return self.driver.find_element(
            By.XPATH, "//button[contains(., 'Execute Meyerhof Calculation')]"
        )

    def status_result_element(self):
        # div dengan binding :class="'status-' + result.status"
        return self.driver.find_element(By.XPATH, "//div[starts-with(@class, 'status-')]")

    def peat_warning_badge(self):
        return self.driver.find_element(
            By.XPATH, "//*[contains(text(), 'PEAT SOIL DETECTED')]"
        )

    def pdf_download_link(self):
        return self.driver.find_element(
            By.XPATH, "//a[contains(., 'Download Technical Report PDF')]"
        )

    def awaiting_execution_placeholder(self):
        return self.driver.find_element(By.XPATH, "//p[text()='Awaiting Execution...']")

    # --- High level actions ---
    def set_value(self, element, value):
        element.clear()
        element.send_keys(str(value))

    def click_calculate(self):
        self.calculate_button().click()

    def wait_for_result(self, timeout=10):
        return WebDriverWait(self.driver, timeout).until(
            EC.visibility_of(self.status_result_element())
        )
