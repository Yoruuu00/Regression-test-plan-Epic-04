import time
import pytest
from selenium.common.exceptions import NoSuchElementException
from page_objects import MeyerhofPage


@pytest.mark.regression
def test_TC01_baseline_calculation_returns_valid_status(meyerhof_page):
    page = MeyerhofPage(meyerhof_page)

    page.set_valid_coordinates()
    page.click_calculate()
    result_el = page.wait_for_result()

    status_text = result_el.text.strip()
    assert status_text in ("LAYAK", "MARGIN", "BAHAYA"), (
        f"Status tidak dikenali: '{status_text}' — kemungkinan ada regresi "
        "pada engine Meyerhof atau kontrak response API berubah."
    )


@pytest.mark.regression
def test_TC05_peat_soil_warning_still_triggers(meyerhof_page):
    payload = {
        "point_label": "TC05-PEAT",
        "qc_values": [10, 10, 10, 10, 10],
        "fs_values": [1, 1, 1, 1, 1],
        "water_content": 500,
        "depth_interval": 1,
        "pile_diameter": 0.4,
        "pile_depth": 3,
        "safety_factor": 3,
        "required_load": 100,
        "sap2000_load": 0,
        "n_pile": 1,
        "m_pile": 1,
        "s_spacing": 1.2,
        "latitude": -7.2575,
        "longitude": 112.7521
    }

    result = meyerhof_page.execute_async_script(
        """
        const payload = arguments[0];
        const done = arguments[arguments.length - 1];

        fetch('/api/projects/1/calculate/meyerhof', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            body: JSON.stringify(payload)
        })
        .then(async response => {
            const json = await response.json().catch(() => ({}));
            done({
                ok: response.ok,
                status: response.status,
                json: json
            });
        })
        .catch(error => {
            done({
                ok: false,
                status: 0,
                error: String(error)
            });
        });
        """,
        payload
    )

    assert result["ok"], (
        f"Request API Meyerhof gagal. Status: {result.get('status')}, "
        f"Response: {result}"
    )

    data = result["json"].get("data", {})

    assert data.get("peat_warning") is True, (
        f"peat_warning seharusnya True ketika water_content=500, "
        f"tapi response: {data}"
    )

    assert data.get("status") == "BAHAYA", (
        f"Status seharusnya BAHAYA ketika water_content=500, "
        f"tapi didapat '{data.get('status')}'."
    )


@pytest.mark.regression
def test_TC11_legacy_form_still_works_with_hardcoded_project(meyerhof_page):
    page = MeyerhofPage(meyerhof_page)

    page.set_valid_coordinates()
    page.click_calculate()
    page.wait_for_result()

    browser_logs = meyerhof_page.execute_script(
        "return window.__testErrors || []"
    )
    assert not browser_logs, f"Ditemukan error JS yang tidak tertangani: {browser_logs}"


@pytest.mark.regression
def test_TC_negative_invalid_pile_depth_does_not_crash(meyerhof_page):
    page = MeyerhofPage(meyerhof_page)

    page.set_valid_coordinates()
    page.set_value(page.pile_depth_input(), 0)
    page.click_calculate()

    time.sleep(2)

    try:
        page.status_result_element()
        pytest.fail("Result panel muncul walau input pile_depth tidak valid.")
    except NoSuchElementException:
        pass


@pytest.mark.regression
def test_TC08_pdf_download_link_present_after_calculation(meyerhof_page):
    page = MeyerhofPage(meyerhof_page)

    page.set_valid_coordinates()
    page.click_calculate()
    page.wait_for_result()

    link = page.pdf_download_link()
    href = link.get_attribute("href")
    assert "/api/calculations/" in href and href.endswith("/pdf"), (
        f"href PDF tidak sesuai pola yang diharapkan: {href}"
    )