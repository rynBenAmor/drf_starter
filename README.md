
# DRF Cookie-Based JWT Starter (with CSRF Protection)

This is a minimal Django REST Framework starter template using **JWT authentication stored in HTTP-only cookies** and **CSRF protection** for secure frontend–backend communication.

---

## Features

* Email & password based authentication
* JWT authentication
* Tokens stored in **secure, HTTP-only cookies**
* Automatic **CSRF protection** for all unsafe HTTP methods
* Login, logout, register, refresh token, and user info endpoints
* CORS configured for cross-origin requests with credentials

---

## Tech Stack

* Django 5
* Django REST Framework
* SimpleJWT
* django-cors-headers

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


| POST   | `/api/accounts/register/`      | Create new user     
| POST   | `/api/accounts/login/`         | Login & set cookies 
| POST   | `/api/accounts/logout/`        | Logout & clear cookies
| GET    | `/api/accounts/me/`            | Get current user info 
| POST   | `/api/accounts/token/refresh/` | Refresh access token  

---

## CSRF Protection

Because JWTs are stored in cookies, **CSRF is enforced** for all unsafe HTTP methods (`POST`, `PUT`, `PATCH`, `DELETE`).

* The backend always sets a `csrftoken` cookie with the `accounts.middlewares.InjectCsrfCookieMiddleware`.
* Frontend must read `csrftoken` and send it in the `X-CSRFToken` header for unsafe requests.

Example fetch:

```js
function getCookie(name) {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) return parts.pop().split(';').shift();
}

fetch('/api/accounts/me/', {
  method: 'PATCH',
  credentials: 'include',
  headers: {
    'Content-Type': 'application/json',
    'X-CSRFToken': getCookie('csrftoken')
  },

});
```

---

## Notes

* `CORS_ALLOW_CREDENTIALS = True` is required so cookies are sent with cross-origin requests.
* `SameSite=None` and `Secure=True` are set on cookies for cross-site HTTPS usage.
