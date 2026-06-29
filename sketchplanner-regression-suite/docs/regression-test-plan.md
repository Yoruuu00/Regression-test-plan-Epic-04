# Regression Test Plan — EPIC-04: Modul Manajemen Proyek & Dashboard Kelayakan

**Sistem**: SketchPlanner (akhmadCh/Sketch-Planner)
**Konteks**: Penambahan fitur yang membutuhkan satu epic, berpotensi memengaruhi modul lain.

---

## 0. Latar Belakang Teknis (temuan dari source code)

Modul yang sudah berjalan saat ini:
- `MeyerhofService` — engine kalkulasi daya dukung tiang (rumus Meyerhof),
  deteksi lahan gambut, efisiensi grup tiang, cek LRFD.
- `SapImportService` — parsing CSV ekspor SAP2000 (kolom Joint/F3).
- `SeismicService` — lookup statis 5 kota (placeholder untuk API PuSGeN).
- `MeyerhofController` + `calculation/meyerhof.blade.php` — UI & API kalkulasi,
  export PDF.

Gap arsitektur yang menjadi pemicu Epic-04:
- Kolom `project_id`, `pile_config_id`, `soil_profile_id` di tabel
  `meyerhof_calculations` **sudah ada tapi tidak punya tabel relasi**.
- Frontend men-**hardcode** `projectId: 1` di Alpine.js state.
- Tidak ada otorisasi proyek, tidak ada dashboard ringkasan, audit trail baru
  sebatas `Log::info` ke file (bukan tabel DB).

## 1. Epic & Change Request yang Dianalisis

**EPIC-04: Modul Manajemen Proyek & Dashboard Kelayakan Multi-Titik Pondasi**

| ID | Story |
|---|---|
| ST-1 | CRUD Proyek (nama, lokasi, koordinat, klien) |
| ST-2 | Relasi formal `MeyerhofCalculation` → `Project` (FK constraint) |
| ST-3 | Dashboard ringkasan % Aman/Margin/Bahaya per proyek |
| ST-4 | Otorisasi akses proyek + berbagi akses tim (US17) |
| ST-5 | SAP2000 import & data seismik terikat konteks proyek |
| ST-6 | PDF report memuat identitas & rekap multi-titik proyek |

Change request teknis yang diperkirakan:
1. Tabel baru `projects` (+`pile_configs`, `soil_profiles`); ALTER FK pada
   `meyerhof_calculations.project_id`.
2. Model `Project`, relasi baru di `MeyerhofCalculation` dan `User`.
3. `ProjectController` baru; `MeyerhofController::calculate()` berubah —
   sekarang wajib validasi `project_id` & otorisasi pengguna.
4. `SeismicService` kemungkinan di-cache per proyek.
5. Frontend `meyerhof.blade.php` (hardcode `projectId:1`) diganti pemilih
   proyek dinamis — **breaking change** untuk alur lama.
6. `calculation/pdf.blade.php` menambah header info proyek.
7. Policy/Gate baru; middleware `auth:sanctum` diperluas.
8. `MeyerhofCalculationObserver` mencatat konteks proyek/kepemilikan.

## 2. Bagian Sistem yang TIDAK BOLEH Terdampak

- Logika inti rumus Meyerhof (`Ap`, `As`, `qc_avg`, `fs_avg`, `qu_kn`, `qa_kn`,
  efisiensi grup, cek LRFD) — toleransi delta < 0.5% (Acceptance Criteria PRD).
- Enum `FoundationStatus` (LAYAK/MARGIN/BAHAYA) dan threshold-nya.
- Logika deteksi lahan gambut (water content 100–1300%, atau Rf>5% & qc<5).
- Parsing CSV SAP2000 (`SapImportService`).
- Nilai statis data gempa 5 kota di `SeismicService`.
- Kolom-kolom lama di `meyerhof_calculations` (hanya boleh ditambah, tidak
  boleh drop/rename).
- Endpoint `/api/user` (Sanctum) yang sudah ada.
- Data kalkulasi lama dengan `project_id = NULL` (backward compatibility).

## 3. Strategi Regression Testing

Pendekatan **risk-based regression**:

1. **Retest-All** untuk engine kalkulasi inti — murah dieksekusi, risiko tinggi.
2. **Selective regression** untuk titik integrasi yang disentuh epic.
3. Layering: Unit (PHPUnit Service layer) → Feature/Integration (Laravel
   `tests/Feature`, termasuk backward-compat `project_id NULL`) → Migration
   test (`up()`/`down()` di salinan data produksi) → E2E (Selenium).
4. Test environment staging dengan seed data lama (`project_id NULL` & `= 1`).
5. CI gate: regression suite wajib hijau sebelum merge PR yang menyentuh
   `app/Services/*`, `app/Http/Controllers/Calculation/*`,
   `database/migrations/*`, `routes/*`.
6. Re-test cycle: bug ditemukan → fix → re-run test gagal + smoke modul
   terkait (bukan full suite).

## 4. Skenario Test-Case Regression

| ID | Modul | Skenario | Hasil Diharapkan |
|---|---|---|---|
| TC-01 | Meyerhof Engine | Hitung dengan parameter baseline | `qu_kn`/`qa_kn` identik baseline (±0.5%) |
| TC-02 | Project–Calculation | Submit dengan `project_id` valid baru | Tersimpan dengan FK benar |
| TC-03 | Validasi | Submit dengan `project_id` tidak ada | Ditolak (404/422) |
| TC-04 | Backward Compat | Baca record lama `project_id = NULL` | Tetap tampil tanpa error |
| TC-05 | Peat Detection | Water content = 500% | Status BAHAYA + `peat_warning=true` |
| TC-06 | SAP2000 Import | Upload `sap2000_test.csv` | `max_load` benar |
| TC-07 | Seismic | GET seismic dekat Banjarmasin | Tetap zone "Low" walau di-cache |
| TC-08 | PDF Report | Download PDF kalkulasi lama | Tergenerate tanpa error null |
| TC-09 | Dashboard | Proyek campuran status | Persentase sesuai data aktual |
| TC-10 | Otorisasi | User A calculate di project User B | Ditolak (403) |
| TC-11 | Frontend Legacy | Buka `/meyerhof_sementara` | Tetap jalan, tanpa error JS |
| TC-12 | Audit Trail | Observer pasca refactor | Log tetap lengkap |
| TC-13 | Non-Functional | 1.000 titik dalam 1 proyek | Tidak ada degradasi performa signifikan |
| TC-14 | Migration | Rollback FK `project_id` | Berhasil tanpa korupsi data |

## 5. Prioritas Pengujian

| Prioritas | Test Case | Alasan |
|---|---|---|
| Kritis | TC-04, TC-10, TC-14 | Integritas/keamanan data antar proyek |
| Tinggi | TC-01, TC-02, TC-03, TC-05, TC-06, TC-08, TC-11 | Akurasi keselamatan struktural & alur harian |
| Sedang | TC-07, TC-09, TC-12 | Fitur pendukung, gagal tidak fatal |
| Rendah | TC-13 | NFR performa |

## 6. Pengukuran Keberhasilan

- Pass rate 100% (Kritis & Tinggi), ≥95% (Sedang).
- Delta numerik Meyerhof vs baseline < 0.5%.
- Defect leakage = 0 untuk severity Kritis/Tinggi saat go-live.
- Code coverage ≥80% pada Service layer yang diubah.
- Audit integrity check 100% pada record baru.
- Sign-off Technical Lead sebelum merge ke `main`.
