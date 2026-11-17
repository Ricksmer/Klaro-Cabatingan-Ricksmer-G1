# Klaro

Klaro is a web-based political information and civic literacy system for Filipino citizens. This repository contains **Project Development 1: the Account Feature**, which the rest of the system will depend on.

- **Course:** CSIT327 Information Management 2
- **Section:** G1
- **Author:** Ricksmer Cabatingan

## Tech Stack

- Full-stack Django (backend and frontend through Django templates)
- PostgreSQL hosted on Supabase
- Django's built-in authentication (hashed passwords)
- Pillow (profile photo uploads)

## Features (Account Feature)

1. **Account Registration**: registration form with required-field checks, email format validation, unique username and email, and password confirmation. Passwords are hashed. Clear success and error messages are shown.
2. **Login / Logout**: log in with email and password, error message on invalid credentials, logout ends the session. Pages that need a logged-in user redirect to the login page.
3. **Role-Based Dashboards**: three roles, each with its own dashboard and navigation. A user cannot open another role's dashboard by typing its URL; they are sent back to their own dashboard.
4. **User Profile**: view and edit your own profile (name, email, contact number, profile photo). Users can only view and edit their own profile.

## User Roles

| Role | How it is assigned | Dashboard |
|---|---|---|
| Admin | Created with `createsuperuser`, or set by an Admin in Django admin | `/dashboard/admin/` |
| Editor | Created or promoted by an Admin in Django admin | `/dashboard/editor/` |
| Citizen | Default role for everyone who registers | `/dashboard/citizen/` |

Self-registration always creates a Citizen. Users cannot change their own role.

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/<your-username>/Klaro-Cabatingan-Ricksmer-G1.git
cd Klaro-Cabatingan-Ricksmer-G1
```

### 2. Create and activate a virtual environment

```bash
python -m venv venv

# Windows (PowerShell)
venv\Scripts\Activate.ps1
# Windows (cmd)
venv\Scripts\activate
# Mac/Linux
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Copy `.env.example` to `.env` (in the same folder as `manage.py`) and fill in your values:

```
SECRET_KEY=
DEBUG=True
DB_NAME=postgres
DB_USER=
DB_PASSWORD=
DB_HOST=
DB_PORT=5432
```

Get the database values from your Supabase project: click **Connect**, choose the **Session pooler** connection string, and split it into the keys above. Generate a secret key with:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

`.env` is listed in `.gitignore` and must never be committed.

### 5. Apply migrations and create an admin

```bash
python manage.py migrate
python manage.py createsuperuser
```

### 6. Run the development server

```bash
python manage.py runserver
```

Open http://127.0.0.1:8000/.

## Creating Editors

1. Log in at http://127.0.0.1:8000/admin/ with the superuser account.
2. Open **Users**, then **Add user**.
3. Enter a username, email, role (`editor`) and password.

## Project Structure

```
Klaro-Cabatingan-Ricksmer-G1/
├── accounts/          # custom User model, forms, views, URLs, role decorator
├── config/            # Django project settings and root URLs
├── templates/
│   ├── base.html
│   ├── _form_fields.html
│   ├── accounts/      # register, login, profile, profile edit
│   └── dashboards/    # admin, editor, citizen
├── manage.py
├── requirements.txt
└── .env.example
```

## Notes

- SQLite is not used. The project requires PostgreSQL (Supabase).
- Uploaded profile photos are stored in a local `media/` folder, which is excluded from Git.
