# Storefront Django Project Setup (Windows)

This guide helps you run this project on a Windows laptop with minimal trial-and-error.
It includes:

- Exact install steps
- Required versions
- Database setup (MySQL)
- Run and verify steps
- Common errors and fixes

---

## 1) Prerequisites

Install these first:

1. **Git for Windows**
   - Download: [https://git-scm.com/download/win](https://git-scm.com/download/win)
2. **Python 3.9.x (64-bit)**
   - Download: [https://www.python.org/downloads/release/python-3913/](https://www.python.org/downloads/release/python-3913/)
   - During install, check **Add Python to PATH**.
3. **MySQL Server 8.0+**
   - Download: [https://dev.mysql.com/downloads/mysql/](https://dev.mysql.com/downloads/mysql/)
   - Remember your MySQL root password.
4. **MySQL Workbench** (optional but helpful)
5. **Visual C++ Build Tools** (only needed if `mysqlclient` build fails)
   - Download: [https://visualstudio.microsoft.com/visual-cpp-build-tools/](https://visualstudio.microsoft.com/visual-cpp-build-tools/)

---

## 2) Open the Project

Use **PowerShell** (recommended) and move to project folder:

```powershell
cd "C:\path\to\storefront"
```

Confirm key files exist:

```powershell
dir manage.py, Pipfile, storefront\settings.py
```

---

## 3) Create and Activate Virtual Environment

You can use either `venv` (simple) or `pipenv` (Pipfile-based).  
Use `venv` for maximum reliability on Windows.

### Option A (recommended): `venv`

```powershell
py -3.9 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip setuptools wheel
```

If PowerShell blocks activation:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Close and reopen PowerShell, then activate again.

### Option B: `pipenv`

```powershell
py -3.9 -m pip install --upgrade pip pipenv
pipenv --python 3.9
pipenv shell
```

---

## 4) Install Python Dependencies

From project root (where `manage.py` exists):

```powershell
pip install django django-debug-toolbar mysqlclient==2.0.3 djangorestframework-simplejwt djoser pillow django-cors-headers django-filter
```

Why `django-filter` here?
- The project settings include `django_filters` in `INSTALLED_APPS`.
- If it is missing, Django fails with `ModuleNotFoundError: No module named 'django_filters'`.

Verify install:

```powershell
pip list | findstr /I "Django mysqlclient djoser pillow django-filter"
```

---

## 5) Configure MySQL Database

Current project settings expect:

- DB Name: `storefront3`
- Host: `localhost`
- User: `root`
- Password: `12345678`

You can either:

1. Set your MySQL root password to `12345678`, **or**
2. Update `storefront\settings.py` with your actual password.

Create database:

```sql
CREATE DATABASE storefront3 CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

From PowerShell CLI:

```powershell
mysql -u root -p -e "CREATE DATABASE IF NOT EXISTS storefront3 CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
```

If `mysql` command not found, add MySQL `bin` to PATH, usually:

`C:\Program Files\MySQL\MySQL Server 8.0\bin`

---

## 6) Run Migrations

```powershell
python manage.py migrate
```

If migration succeeds, create admin user:

```powershell
python manage.py createsuperuser
```

---

## 7) (Optional) Seed Initial Data

This project includes a seed command:

```powershell
python manage.py seed_db
```

Use this only after migrations are complete.

---

## 8) Run Development Server

```powershell
python manage.py runserver
```

Open:

- API/Admin home: [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)
- Debug toolbar appears in DEBUG mode.

Stop server with `Ctrl + C`.

---

## 9) Smoke Test Checklist (No-error verification)

Run these in order:

1. `python --version` -> should be 3.9.x
2. `python manage.py check` -> no critical issues
3. `python manage.py migrate` -> OK
4. `python manage.py runserver` -> starts without traceback
5. Visit `/admin/` -> login page loads
6. Login with superuser -> admin dashboard opens

If all pass, project setup is working.

---

## 10) Troubleshooting (Common Windows Errors)

### Error A: `ModuleNotFoundError: No module named 'django_filters'`

Fix:

```powershell
pip install django-filter
```

---

### Error B: `ModuleNotFoundError: No module named 'MySQLdb'`

Cause: `mysqlclient` not installed correctly.

Fix sequence:

1. Ensure you are in activated virtual environment.
2. Upgrade build tools:

```powershell
python -m pip install --upgrade pip setuptools wheel
```

3. Install Visual C++ Build Tools.
4. Retry:

```powershell
pip install mysqlclient==2.0.3
```

If still failing, install latest compatible version:

```powershell
pip install mysqlclient
```

---

### Error C: `django.db.utils.OperationalError: (1045, "Access denied for user 'root'@'localhost'")`

Cause: Wrong DB credentials in `storefront\settings.py`.

Fix:

- Update `DATABASES['default']['PASSWORD']` to actual MySQL password.
- Or create a dedicated DB user and update `USER`/`PASSWORD`.

Example SQL:

```sql
CREATE USER 'storefront_user'@'localhost' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON storefront3.* TO 'storefront_user'@'localhost';
FLUSH PRIVILEGES;
```

Then update Django settings accordingly.

---

### Error D: `Unknown database 'storefront3'`

Fix:

```powershell
mysql -u root -p -e "CREATE DATABASE storefront3 CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
python manage.py migrate
```

---

### Error E: `ERROR 2003 (HY000): Can't connect to MySQL server`

Fix:

- Start MySQL service from Windows Services (`services.msc`) or MySQL Workbench.
- Confirm host/port (`localhost:3306`).
- Check firewall or another app using the same port.

---

### Error F: `python` points to wrong version

Fix:

```powershell
py -0p
py -3.9 -m venv .venv
.\.venv\Scripts\Activate.ps1
python --version
```

If still wrong, remove older conflicting Python from PATH.

---

### Error G: PowerShell script execution blocked

Fix:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Restart terminal and activate venv again.

---

## 11) Recommended Improvement (Optional but safer)

For cleaner local setup, move DB credentials to environment variables and do not keep passwords hardcoded in `settings.py`.

Until then, setup must match current hardcoded values in project settings.

