# DRF Hybrid JWT Starter

This project is a minimal Django REST Framework setup that supports a flexible authentication workflow. You can authenticate with either:

- JWT access tokens stored in **HTTP-only cookies** (with full CSRF protection)
- Standard **Bearer tokens** sent through the Authorization header.

This structure works well for browser-based apps, SPAs, mobile clients, or any mixed environment.

---

## Features

- Email and password authentication
- JWT authentication using SimpleJWT
- Access tokens stored in secure, HTTP-only cookies
- Automatic CSRF protection for unsafe HTTP methods
- Login, logout, register, refresh, and current user endpoints
- CORS configured for cross-origin requests with credentials

---

## Tech Stack

- Django 5
- Django REST Framework
- SimpleJWT
- django-cors-headers (optional if you handle CORS in a reverse proxy like Nginx)

---

## Installation

```bash
git clone https://github.com/rynBenAmor/drf_starter.git
cd drf_starter
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

---

## Endpoints

| Method | Endpoint                       | Description                |
| ------ | ------------------------------ | -------------------------- |
| POST   | `/api/accounts/register/`      | Register a new user        |
| POST   | `/api/accounts/login/`         | Log in and set cookies     |
| POST   | `/api/accounts/logout/`        | Log out and clear cookies  |
| GET    | `/api/accounts/me/`            | Get the authenticated user |
| POST   | `/api/accounts/token/refresh/` | Refresh the access token   |

---

## CSRF Protection

Since JWTs are stored in cookies, CSRF protection is enforced for all unsafe requests (`POST`, `PUT`, `PATCH`, `DELETE`).

- A CSRF cookie is always set by `InjectCsrfCookieMiddleware`.
- The frontend must read that cookie and send its value in the `X-CSRFToken` header.

Example:

```js
function getCookie(name) {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) return parts.pop().split(";").shift();
}

fetch("/api/accounts/me/", {
  method: "GET",
  credentials: "include",
  headers: {
    "Content-Type": "application/json",
    "X-CSRFToken": getCookie("csrftoken"),
  },
});
```

---

## Notes

- `CORS_ALLOW_CREDENTIALS = True` is required so cookies are sent with cross-origin requests.
- Cookies use `SameSite=None` and `Secure=True` so they work across domains over HTTPS.
- Create a `.env` file before running the project.

---

## Example `.env`

<details>
<summary>Click to expand</summary>

```env
EMAIL_HOST_USER="fake@fake.fake"
DEFAULT_FROM_EMAIL="fake@fake.fake"
EMAIL_HOST_PASSWORD="fake app password"
EMAIL_PORT=587

DJANGO_IS_PRODUCTION=False
# You can use: python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
DJANGO_SECRET_KEY="django-insecure-123"
DJANGO_ADMIN_EMAIL_1=""

CORS_ALLOWED_ORIGINS=http://localhost:5173
ALLOWED_HOSTS=localhost,127.0.0.1,

DB_TYPE='sqlite'
DB_NAME=''
DB_USER=''
DB_PASSWORD=''
DB_HOST=localhost
DB_PORT=5432
```

</details>

---
