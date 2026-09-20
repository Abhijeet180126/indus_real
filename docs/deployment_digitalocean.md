# Deploying to a DigitalOcean Droplet

Steps to put this Django app (Indus-Reality) on a production DigitalOcean Droplet,
serving it with **uWSGI + Nginx**, HTTPS via **Let's Encrypt**, and a systemd
service (named `indusreal`) so it survives reboots.

This targets a single Ubuntu 24.04 LTS droplet. SQLite (the current database) is fine
for a small single-server site — no managed database needed.

**This droplet already runs another app.** This guide keeps the two fully separate:
this app listens on `127.0.0.1:8000` (Django's default port) and is reached through
its own domain/subdomain in Nginx — it does not touch the other app's port, systemd
service, or Nginx server block. Before starting, confirm port 8000 is actually free:

```bash
sudo ss -tlnp | grep 8000
```

If something's already using 8000, pick a different free port and use it consistently
in step 9 (`socket =`) and step 10 (`uwsgi_pass`) below.

---

## 1. Create the Droplet

1. In the DigitalOcean dashboard: **Create → Droplets**.
2. Image: **Ubuntu 24.04 (LTS) x64**.
3. Plan: Basic, Regular SSD, **1 GB RAM / 1 vCPU** is enough to start (upgrade later if needed).
4. Authentication: **SSH key** (add your public key) rather than a password.
5. Hostname: e.g. `indus-reality`.
6. Create the droplet and note its public IP.

## 2. Point DNS at the droplet

This app needs its own domain or subdomain — separate from whatever URL the other app
on this droplet already answers to. Example used throughout this guide:
`indusreal.yourdomain.com` (swap in a domain/subdomain you actually own).

In your domain registrar / DNS provider, add:

- `A` record: `indusreal` (or whatever subdomain you're using) → droplet IP

(Or use DigitalOcean's own DNS by adding the domain under **Networking → Domains** and
pointing your registrar's nameservers at DigitalOcean.) Since the droplet's IP is
already serving another app, both domains simply point at the same IP — Nginx
separates them by `server_name`, not by IP or port.

## 3. Initial server setup

SSH in as root, then create a non-root sudo user and lock down SSH:

```bash
ssh root@YOUR_DROPLET_IP

adduser deploy
usermod -aG sudo deploy

# Basic firewall
ufw allow OpenSSH
ufw allow 'Nginx Full'
ufw enable

# Copy your SSH key to the new user, then disable root/password login
rsync --archive --chown=deploy:deploy ~/.ssh /home/deploy
```

Edit `/etc/ssh/sshd_config`: set `PermitRootLogin no`, `PasswordAuthentication no`, then
`systemctl restart ssh`. From here on, log in as `deploy`.

## 4. Install system packages

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3-venv python3-pip nginx git
```

## 5. Get the code onto the server

```bash
sudo mkdir -p /var/www/indus-reality
sudo chown deploy:deploy /var/www/indus-reality
cd /var/www/indus-reality

# Push your local repo to the server, or clone from your git remote:
git clone <your-repo-url> .
```

If you don't have a git remote yet, push from your machine with `rsync` instead:

```bash
# from your local machine
rsync -avz --exclude venv --exclude db.sqlite3 --exclude staticfiles \
  D:/Indus/real/ deploy@YOUR_DROPLET_IP:/var/www/indus-reality/
```

## 6. Python environment

```bash
cd /var/www/indus-reality
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pip install uwsgi
```

Add `uwsgi` to `requirements.txt` (`pip freeze | grep -i uwsgi >> requirements.txt`) so future
deploys pick it up.

No app-side static file serving package is needed — Nginx serves `/static/` and `/media/`
directly from disk (configured in step 10), so Django never handles those requests in
production.

## 7. Configure environment variables

```bash
cp .env.example .env
nano .env
```

Set at minimum:

```
DJANGO_SECRET_KEY=<generate a new 50-char random value>
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=indusreal.yourdomain.com

EMAIL_PROVIDER=ses            # or smtp — see .env.example
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
AWS_SES_REGION_NAME=us-east-1
DEFAULT_FROM_EMAIL=noreply@yourdomain.com
CONTACT_TO_EMAIL=you@yourdomain.com
```

Generate a fresh secret key:

```bash
python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

## 8. Django setup: migrate, collectstatic, superuser

```bash
source venv/bin/activate
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser
```

Make sure `media/` (uploaded property images) and `db.sqlite3` are writable by the
app user and are **not** wiped by future deploys — they hold real data.

## 9. uWSGI as a systemd service (`indusreal`)

Create `/var/www/indus-reality/indusreal.ini`:

```ini
[uwsgi]
chdir = /var/www/indus-reality
module = realestate.wsgi:application
home = /var/www/indus-reality/venv

master = true
processes = 3
socket = 127.0.0.1:8000
vacuum = true
die-on-term = true
```

`socket` here binds uWSGI to a local TCP port (using the uwsgi protocol, paired with
`uwsgi_pass` in Nginx) rather than a unix socket file — this keeps it independent of
the other app running on the droplet.

cat /etc/systemd/system/indus-real.service

---------------------------------------------------

[Unit]
Description=Indus Reality Django Gunicorn
After=network.target

[Service]
User=root
Group=root

WorkingDirectory=/var/www/indus-reality/indus_real

EnvironmentFile=/var/www/indus-reality/indus_real/.env

Environment="PATH=/var/www/indus-reality/indus_real/venv/bin"

ExecStart=/var/www/indus-reality/indus_real/venv/bin/gunicorn \
    --workers 3 \
    --bind 127.0.0.1:8000 \
    realestate.wsgi:application

Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target


----------------------------------

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now indus-real
sudo systemctl status indus-real
```

## 10. Nginx reverse proxy

This adds a **new, independent server block** — it doesn't touch the existing app's
config, and there's no server-block naming collision as long as `server_name` differs.

cat /etc/nginx/sites-available/indusrealty.org
server {

    server_name indusrealty.org www.indusrealty.org;

    client_max_body_size 20M;
        # Django static files 
    location /static/ { 
            alias /var/www/indus-reality/indus_real/staticfiles/; 
    }
    location /media/ {
        alias /var/www/indus-reality/indus_real/media/;
}

    location / {
        proxy_pass http://127.0.0.1:8000;

        proxy_http_version 1.1;

        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    listen 443 ssl; # managed by Certbot
    listen [::]:443 ssl; # managed by Certbot
    ssl_certificate /etc/letsencrypt/live/indusrealty.org/fullchain.pem; # managed by Certbot
    ssl_certificate_key /etc/letsencrypt/live/indusrealty.org/privkey.pem; # managed by Certbot
    include /etc/letsencrypt/options-ssl-nginx.conf; # managed by Certbot
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem; # managed by Certbot


}

server {
    if ($host = www.indusrealty.org) {
        return 301 https://$host$request_uri;
    } # managed by Certbot


    if ($host = indusrealty.org) {
        return 301 https://$host$request_uri;
    } # managed by Certbot


    listen 80;
    listen [::]:80;

    server_name indusrealty.org www.indusrealty.org;
    return 404; # managed by Certbot




}
```bash
sudo ln -s /etc/nginx/sites-available/indus-reality /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

(Don't remove `sites-enabled/default` or touch the other app's site file here — leave
its config as-is.)

Site should now be reachable over plain HTTP at `indusreal.yourdomain.com`.

## 11. HTTPS with Let's Encrypt

```bash
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d indusreal.yourdomain.com
```

(Skip `apt install certbot...` if certbot is already installed for the other app —
just run the `certbot --nginx -d ...` command for this new domain.)

Certbot edits the Nginx config to redirect HTTP → HTTPS and sets up auto-renewal
(`systemctl status certbot.timer` to confirm).

## 12. Verify

- Visit `https://indusreal.yourdomain.com/` — site loads, padlock is valid.
- Visit `https://indusreal.yourdomain.com/admin/` — log in with the superuser you created.
- Submit the contact form — check it arrives by email (or check `ContactMessage` in
  the admin) and check `sudo journalctl -u indusreal -n 50` for errors if not.
- Confirm the other app on the droplet is still unaffected (its own URL still loads).

## 13. Deploying updates later

```bash
cd /var/www/indus-reality
git pull                      # or rsync new files
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
sudo systemctl restart indusreal
```

## 14. Backups

SQLite + `media/` live only on this droplet's disk, so back them up regularly:

```bash
# quick manual backup
tar czf backup-$(date +%F).tar.gz db.sqlite3 media/
```

Consider a cron job that copies this tarball to DigitalOcean Spaces (or another
off-server location) on a schedule, and/or enabling DigitalOcean's droplet-level
**Backups** or **Snapshots** in the dashboard.

## Notes specific to this project

- `requirements.txt` doesn't currently include `uwsgi` — added in step 6 above for this
  deployment. Static/media files are served directly by Nginx (step 10), no extra
  Django-side static file package needed.
- This app is fully isolated from the other app already on the droplet: separate
  systemd service (`indusreal`), separate local port (`127.0.0.1:8000`), separate
  Nginx server block keyed off its own `server_name`, and its own domain/subdomain.
  Nothing here modifies the other app's service, port, or Nginx config.
- `EMAIL_PROVIDER` in `.env` controls whether contact-form email goes via Amazon SES,
  plain SMTP, or (if unset) just prints to console — see `.env.example` for both options.
  On a fresh droplet with no `EMAIL_PROVIDER` set, emails will silently only log to
  console, not actually send.
- `DJANGO_DEBUG` defaults to `False` in code, but set it explicitly in `.env` anyway.
