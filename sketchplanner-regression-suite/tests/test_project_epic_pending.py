"""
Skenario Selenium untuk fitur-fitur di EPIC-04 (Modul Manajemen Proyek &
Dashboard Kelayakan) yang BELUM diimplementasikan di UI saat ini.

Test ini ditulis lebih dulu (sebelum fitur dibangun) dengan tujuan:
1. Menjadi spesifikasi yang jelas & dapat dieksekusi (executable spec) bagi
   developer yang mengerjakan epic ini.
2. Menjadi checklist "Definition of Done" untuk regression sign-off — hapus
   marker @pytest.mark.skip begitu elemen UI terkait sudah dirilis ke
   environment staging, lalu lengkapi locator-nya.

Lihat docs/regression-test-plan.md TC-02, TC-03, TC-09, TC-10.
"""
import pytest
from selenium.webdriver.common.by import By


pytestmark = pytest.mark.epic04_pending


@pytest.mark.skip(reason="UI manajemen proyek (ST-1) belum dirilis")
def test_TC02_calculation_saved_under_correct_project(driver):
    """
    TC-02: Setelah Epic-04 rilis, pengguna memilih/membuat proyek baru lewat
    UI, lalu melakukan kalkulasi. Record yang tersimpan harus terikat ke
    project_id proyek yang sedang aktif (bukan lagi hardcode = 1).
    """
    # TODO setelah ST-1 & ST-2 rilis:
    # 1. driver.get(f"{BASE_URL}/projects")
    # 2. Buat proyek baru via form, ambil project_id dari URL/elemen hasil
    # 3. Masuk ke halaman kalkulasi proyek tersebut
    # 4. Jalankan kalkulasi, assert response/record memakai project_id ini
    pass


@pytest.mark.skip(reason="Validasi project_id tidak valid (ST-2) belum dirilis di UI")
def test_TC03_invalid_project_id_rejected(driver):
    """
    TC-03: Mengakses URL kalkulasi dengan project_id yang tidak ada di
    database harus menampilkan pesan error yang jelas, bukan crash atau
    diterima diam-diam seperti behaviour lama.
    """
    pass


@pytest.mark.skip(reason="Dashboard ringkasan kelayakan (ST-3) belum dirilis")
def test_TC09_dashboard_percentage_matches_actual_points(driver):
    """
    TC-09: Dashboard proyek dengan kombinasi titik berstatus
    LAYAK/MARGIN/BAHAYA harus menampilkan persentase yang sesuai dengan
    jumlah titik aktual di proyek tersebut.
    """
    pass


@pytest.mark.skip(reason="Otorisasi akses proyek (ST-4) belum dirilis")
def test_TC10_user_cannot_access_other_users_project(driver):
    """
    TC-10: User A login dan mencoba mengakses/menghitung pada proyek milik
    User B (tanpa diundang/diberi akses) harus ditolak (403), bukan
    menampilkan data proyek tersebut. Ini regression guard terhadap
    kebocoran data antar klien konstruksi.
    """
    pass
