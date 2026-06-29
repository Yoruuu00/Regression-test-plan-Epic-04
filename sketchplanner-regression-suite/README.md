# SketchPlanner — Regression Test Suite (Selenium)

Repo ini berisi **regression test plan** dan **Selenium test suite** untuk
mengawal **EPIC-04: Modul Manajemen Proyek & Dashboard Kelayakan Multi-Titik
Pondasi** pada aplikasi [Sketch-Planner](https://github.com/akhmadCh/Sketch-Planner)
agar tidak merusak modul yang sudah berjalan (engine Meyerhof, deteksi lahan
gambut, import SAP2000, data gempa, export PDF).

## Isi Repo

```
.
├── docs/
│   └── regression-test-plan.md   # analisis CR, scope boundary, strategi,
│                                  # 14 skenario test, prioritas, success metric
├── tests/
│   ├── conftest.py               # fixture WebDriver
│   ├── test_meyerhof_regression.py        # skenario yang BISA dijalankan sekarang
│   └── test_project_epic_pending.py       # skenario yang menunggu Epic-04 rilis
├── requirements.txt
├── pytest.ini
└── .github/workflows/regression-ci.yml    # CI gate otomatis
```

## Catatan Penting tentang Testability

Form `meyerhof.blade.php` saat ini dibangun dengan Alpine.js dan **tidak punya
atribut `id`, `name`, atau `data-testid`** pada input-nya — hanya `x-model`.
Karena itu locator di test ini memakai XPath relatif ke teks label
(`//label[text()='...']/following-sibling::input`), yang **rapuh** terhadap
perubahan teks/struktur HTML.

**Rekomendasi sebelum Epic-04 dikerjakan**: tambahkan atribut
`data-testid="point-label-input"`, dst. pada setiap input/button penting.
Ini item kecil tapi akan sangat menstabilkan automation jangka panjang.

## Menjalankan Test

```bash
pip install -r requirements.txt
# pastikan ChromeDriver tersedia & app berjalan di BASE_URL
export BASE_URL="http://localhost:8000"
pytest -v
```

Test yang menyentuh fitur Epic-04 (manajemen proyek, dashboard, otorisasi)
ditandai `@pytest.mark.skip` karena UI-nya belum ada. Hapus marker tersebut
begitu fitur terkait sudah dirilis ke environment staging — gunakan ini
sebagai checklist "Definition of Done" untuk regression sign-off.

## Cara Push ke GitHub Anda

```bash
git init
git add .
git commit -m "Regression test plan & Selenium suite for Epic-04"
git branch -M main
git remote add origin https://github.com/<username>/<nama-repo-baru>.git
git push -u origin main
```

Atau, jika ingin ditaruh sebagai sub-folder di repo `Sketch-Planner` yang sudah
ada, salin folder ini ke `tests/regression/selenium/` lalu commit di branch
fitur Epic-04.
