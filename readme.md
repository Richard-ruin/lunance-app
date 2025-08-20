📌 Tutorial Instalasi & Menjalankan Project

1. Setup Backend

Buka Terminal 1, lalu:

cd backend

a. Buat Virtual Environment (venv)
python -m venv venv

b. Aktifkan venv

Windows (CMD / PowerShell):

venv\Scripts\activate

Linux / macOS:

source venv/bin/activate

c. Install Requirements
pip install -r requirements.txt

d. (Opsional) Jalankan Fine-tune Script
python scripts/train/main.py

e. Jalankan Backend (FastAPI dengan Uvicorn)
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

2. Setup Frontend

Buka Terminal 2, lalu:

cd lunance

a. Install Dependencies Flutter
flutter pub get

b. Jalankan Aplikasi Flutter
flutter run

3. Alur Menjalankan Project

Terminal 1 → Backend aktif di http://localhost:8000

Terminal 2 → Frontend Flutter jalan di emulator/device
