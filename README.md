# Indus-Reality (Django real estate site)

## Setup

```
python -m venv venv
venv\Scripts\activate          # Windows
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Visit http://127.0.0.1:8000/ for the site and http://127.0.0.1:8000/admin/ to manage listings.

## Structure

- `listings` app — `Property`, `PropertyImage`, `Amenity` models. Manage all listings from the Django admin (add photos, mark featured, mark sold/rented, etc). No coding needed to update inventory.
- `pages` app — Home page, Contact Us page/form, `ContactMessage` model (inquiries also appear in the admin under Pages).
- Bootstrap 5 (via CDN) for styling, in `templates/base.html`.
- SQLite by default (`db.sqlite3`), uploaded images saved under `media/`.

## Email for the contact form

By default, contact form emails print to the console (dev-friendly, no setup). To actually send emails, set these environment variables before starting the server:

```
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=you@example.com
EMAIL_HOST_PASSWORD=your-app-password
EMAIL_USE_TLS=True
CONTACT_TO_EMAIL=client@example.com
```

Every inquiry is always saved to the database (visible in the admin) regardless of whether email sending is configured.

## Before deploying

- Set `DJANGO_SECRET_KEY`, `DJANGO_DEBUG=False`, and `DJANGO_ALLOWED_HOSTS` as environment variables.
- Configure real email credentials (above).
- Serve static/media files properly (e.g. WhiteNoise + a cloud storage backend, or your host's static file handling) — SQLite and local media storage are fine for a small single-server deployment but won't survive on platforms with ephemeral filesystems (e.g. Heroku).
