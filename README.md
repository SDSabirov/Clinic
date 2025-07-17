# Clinic Management API

This project is a simple Django REST Framework backend for a clinic management system. It provides authentication with JWT tokens, user profiles for doctors and receptionists, and endpoints for managing patients and appointment bookings.

## Features

- Custom `User` model with roles (doctor or receptionist).
- Endpoints to register a user together with their profile.
- JWT based authentication using `djangorestframework-simplejwt`.
- CRUD APIs for patients and booking appointments.
- Profile endpoints for doctors and receptionists.

## Requirements

- Python 3.11+
- Django 5.2
- Django REST Framework
- djangorestframework-simplejwt
- django-environ

## Setup

1. Create and activate a virtual environment:

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

2. Install dependencies:

   ```bash
   pip install django djangorestframework djangorestframework-simplejwt django-environ
   ```

3. Create a `.env` file in the project root and define at least:

   ```env
   SECRET_KEY=your-secret-key
   DEBUG=True
   ALLOWED_HOSTS=localhost,127.0.0.1
   ```

4. Apply migrations and create a superuser:

   ```bash
   python manage.py migrate
   python manage.py createsuperuser
   ```

5. Run the development server:

   ```bash
   python manage.py runserver
   ```

## API Endpoints

Base API path: `/api/`

- `POST /api/login/` – obtain access and refresh JWT tokens.
- `POST /api/profiles/register/` – register a user with a doctor or receptionist profile.
- `GET|PATCH /api/profiles/me/` – retrieve or update the authenticated user's profile.
- `GET|POST /api/patients/` – manage patients.
- `GET|POST /api/bookings/` – manage appointment bookings.

The browsable API can be accessed while DEBUG is enabled.

## Running Tests

Run the test suite with:

```bash
pytest -q
```

*(Note: Tests are minimal and may require additional dependencies.)*

