from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class MeyerhofPage:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)

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
        return self.driver.find_element(
            By.XPATH, "//div[starts-with(@class, 'status-')]"
        )

    def peat_warning_badge(self):
        return self.driver.find_elements(
            By.XPATH, "//*[contains(., 'PEAT') or contains(., 'GAMBUT') or contains(., 'gambut')]"
        )

    def pdf_download_link(self):
        return self.driver.find_element(
            By.XPATH, "//a[contains(., 'Download Technical Report PDF')]"
        )

    def awaiting_execution_placeholder(self):
        return self.driver.find_element(
            By.XPATH, "//p[text()='Awaiting Execution...']"
        )

    def set_value(self, element, value):
        element.clear()
        element.send_keys(str(value))

    def set_alpine_values(self, values):
        script = """
        const roots = document.querySelectorAll('[x-data]');
        let updated = 0;

        for (const root of roots) {
            let data = null;

            if (root.__x && root.__x.$data) {
                data = root.__x.$data;
            }

            if (!data && root._x_dataStack && root._x_dataStack.length > 0) {
                data = root._x_dataStack[0];
            }

            if (data) {
                for (const [key, value] of Object.entries(arguments[0])) {
                    data[key] = value;
                }
                updated++;
            }
        }

        return updated > 0;
        """

        success = self.driver.execute_script(script, values)

        if not success:
            raise Exception("Gagal mengisi data Alpine.")

    def set_valid_coordinates(self, latitude=-7.2575, longitude=112.7521):
        self.set_alpine_values({
            "latitude": float(latitude),
            "longitude": float(longitude)
        })

    def set_water_content(self, value):
        self.set_alpine_values({
            "waterContent": float(value),
            "water_content": float(value)
        })

    def force_peat_soil_payload(self):
        script = """
        if (!window.__peatPayloadPatched) {
            const originalFetch = window.fetch;

            window.fetch = function(input, init) {
                if (
                    init &&
                    init.method &&
                    init.method.toUpperCase() === 'POST' &&
                    typeof input === 'string' &&
                    input.includes('/calculate/meyerhof') &&
                    init.body
                ) {
                    const body = JSON.parse(init.body);

                    body.latitude = -7.2575;
                    body.longitude = 112.7521;
                    body.water_content = 500;
                    body.waterContent = 500;

                    if (!body.cpt_data || !Array.isArray(body.cpt_data)) {
                        body.cpt_data = [
                            {"depth": 1, "qc": 10, "fs": 1},
                            {"depth": 2, "qc": 10, "fs": 1},
                            {"depth": 3, "qc": 10, "fs": 1}
                        ];
                    }

                    init.body = JSON.stringify(body);
                }

                return originalFetch.call(this, input, init);
            };

            window.__peatPayloadPatched = true;
        }

        return true;
        """

        self.driver.execute_script(script)

    def click_calculate(self):
        self.calculate_button().click()

    def wait_for_result(self, timeout=10):
        return WebDriverWait(self.driver, timeout).until(
            EC.visibility_of_element_located(
                (By.XPATH, "//div[starts-with(@class, 'status-')]")
            )
        )