"""
Regression test untuk modul yang SUDAH BERJALAN saat ini (Meyerhof Engine,
deteksi lahan gambut, validasi input, PDF link).

Tujuan: dijalankan SEBELUM dan SETELAH Epic-04 (Modul Manajemen Proyek)
dikerjakan, untuk memastikan modul-modul ini tidak ikut rusak walau tidak
termasuk dalam scope epic (lihat docs/regression-test-plan.md bagian 2).
"""
import pytest
from page_objects import MeyerhofPage


@pytest.mark.regression
def test_TC01_baseline_calculation_returns_valid_status(meyerhof_page):
    """
    TC-01: Kalkulasi dengan parameter default (mock data sondir auto-generate)
    harus menghasilkan status valid tanpa error, terlepas dari perubahan
    di modul manajemen proyek.
    """
    page = MeyerhofPage(meyerhof_page)

    page.click_calculate()
    result_el = page.wait_for_result()

    status_text = result_el.text.strip()
    assert status_text in ("LAYAK", "MARGIN", "BAHAYA"), (
        f"Status tidak dikenali: '{status_text}' — kemungkinan ada regresi "
        "pada engine Meyerhof atau kontrak response API berubah."
    )


@pytest.mark.regression
def test_TC05_peat_soil_warning_still_triggers(meyerhof_page):
    """
    TC-05: Input water content dalam rentang 100-1300% harus tetap memicu
    badge peringatan lahan gambut (US03), terlepas dari konteks proyek mana
    pun kalkulasi ini berada.
    """
    page = MeyerhofPage(meyerhof_page)

    page.set_value(page.water_content_input(), 500)
    page.click_calculate()
    page.wait_for_result()

    badge = page.peat_warning_badge()
    assert badge.is_displayed(), (
        "Badge 'PEAT SOIL DETECTED' tidak muncul — regresi pada logika "
        "deteksi lahan gambut (US03), ini fitur safety-critical."
    )

    status_el = page.status_result_element()
    assert status_el.text.strip() == "BAHAYA", (
        "Status seharusnya BAHAYA ketika tanah gambut terdeteksi, "
        f"tapi didapat '{status_el.text.strip()}'."
    )


@pytest.mark.regression
def test_TC11_legacy_form_still_works_with_hardcoded_project(meyerhof_page):
    """
    TC-11: Form lama (yang masih meng-hardcode projectId=1 di Alpine.js)
    harus tetap berfungsi setelah backend menambahkan validasi project_id
    untuk Epic-04. Ini guard penting karena frontend lama BELUM diupdate
    untuk memilih proyek secara dinamis.
    """
    page = MeyerhofPage(meyerhof_page)

    page.click_calculate()
    page.wait_for_result()  # akan timeout & gagal jika request ke
                             # /api/projects/1/calculate/meyerhof mulai ditolak

    browser_logs = meyerhof_page.execute_script(
        "return window.__testErrors || []"
    )
    assert not browser_logs, f"Ditemukan error JS yang tidak tertangani: {browser_logs}"


@pytest.mark.regression
def test_TC_negative_invalid_pile_depth_does_not_crash(meyerhof_page):
    """
    Skenario negatif (pendukung TC-03): pile_depth di luar rentang valid
    (server-side rule: min:0.2, max:60) harus ditangani dengan errorMsg,
    bukan membuat halaman crash atau result panel tampil dengan data salah.
    """
    page = MeyerhofPage(meyerhof_page)

    page.set_value(page.pile_depth_input(), 0)  # invalid, di bawah min:0.2
    page.click_calculate()

    # Result panel TIDAK seharusnya muncul untuk input invalid
    from selenium.common.exceptions import NoSuchElementException
    import time
    time.sleep(2)  # beri waktu request gagal & errorMsg di-set
    try:
        page.status_result_element()
        pytest.fail("Result panel muncul walau input pile_depth tidak valid.")
    except NoSuchElementException:
        pass  # diharapkan: tidak ada result, karena validasi server menolak


@pytest.mark.regression
def test_TC08_pdf_download_link_present_after_calculation(meyerhof_page):
    """
    TC-08: Setelah kalkulasi sukses, link download PDF harus tersedia dan
    mengarah ke endpoint /api/calculations/{id}/pdf yang valid — termasuk
    untuk kalkulasi yang dibuat sebelum Epic-04 (tanpa konteks proyek penuh).
    """
    page = MeyerhofPage(meyerhof_page)

    page.click_calculate()
    page.wait_for_result()

    link = page.pdf_download_link()
    href = link.get_attribute("href")
    assert "/api/calculations/" in href and href.endswith("/pdf"), (
        f"href PDF tidak sesuai pola yang diharapkan: {href}"
    )
