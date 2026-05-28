# Ultimate Guide to Free-Forever Hosting on Oracle Cloud Infrastructure (OCI)

This guide provides a detailed, step-by-step walkthrough of how to host this Django-based storefront project (including Django, MySQL, Redis, Celery Worker, and Celery Beat) **100% free forever**, without any automated database wipes or idle-sleep timeouts.

---

## Table of Contents

1. [Why Oracle Cloud (OCI) is the Best Choice](#1-why-oracle-cloud-oci-is-the-best-choice)
2. [Step 1: Sign up for OCI Always Free](#step-1-sign-up-for-oci-always-free)
3. [Step 2: Provision Your Always-Free Compute Instance](#step-2-provision-your-always-free-compute-instance)
4. [Step 3: Configure Cloud Network (VCN) Firewalls](#step-3-configure-cloud-network-vcn-firewalls)
5. [Step 4: Connect to Your VM and Configure OS Firewalls](#step-4-connect-to-your-vm-and-configure-os-firewalls)
6. [Step 5: Prepare the Django Project for Production](#step-5-prepare-the-django-project-for-production)
7. [Step 6: Production-Ready Docker & Docker-Compose Setup](#step-6-production-ready-docker--docker-compose-setup)
8. [Step 7: Deploy and Set Up Let's Encrypt SSL](#step-7-deploy-and-set-up-lets-encrypt-ssl)
9. [Step 8: Prevent Oracle VM Reclamation (Crucial!)](#step-8-prevent-oracle-vm-reclamation-crucial)
10. [Backup & Maintenance](#backup--maintenance)

---

## 1. Why Oracle Cloud (OCI) is the Best Choice

Most "free" platforms have catches that make them unsuitable for hosting a production-grade backend:

- **Render / Heroku / Fly.io / Railway**: Free web services go to sleep after 15 minutes of inactivity (causing 30-second cold starts). Worse, Render **permanently deletes/wipes free PostgreSQL databases after 90 days**.
- **Supabase / Neon**: Free tiers automatically pause databases after 1-2 weeks of inactivity.
- **Oracle Cloud (OCI) Always Free**:
  - **Ampere A1 Compute VM**: Up to **4 OCPUs (ARM64) and 24 GB of RAM** with up to **200 GB NVMe SSD storage**.
  - **Network**: **10 TB** of outbound data transfer per month.
  - **Database**: By running MySQL/Redis inside Docker containers on your VM, your database lives on your 200 GB SSD storage. **It will never be wiped, cleared, or paused**, and you have full superuser control.

---

## Step 1: Sign up for OCI Always Free

1. Go to [oracle.com/cloud/free](https://www.oracle.com/cloud/free/).
2. Click **Start for free**.
3. Fill in your details. **Crucial:** Select your **Home Region** carefully. You cannot change it later, and Always-Free Ampere VM capacity is sometimes scarce in certain regions. (E.g., choose a region close to your users).
4. Enter payment details for identity verification. Oracle will place a temporary charge (~$1) which is instantly refunded. You will **never** be charged unless you manually upgrade to a paid account.

---

## Step 2: Provision Your Always-Free Compute Instance

Once logged into your OCI Console:

1. Click the hamburger menu (top-left) ➔ **Compute** ➔ **Instances**.
2. Click **Create instance**.
3. **Configure settings:**
   - **Name**: `storefront-prod`
   - **Placement / Availability Domain**: Keep default.
   - **Image and shape**:
     - Click **Edit**.
     - Click **Change Image** and select **Ubuntu 22.04 LTS** or **Ubuntu 24.04 LTS** (highly recommended for Docker compatibility).
     - Click **Change Shape**. Select **Ampere (ARM-based)**. Check **VM.Standard.A1.Flex**.
     - Set OCPUs to **2** and Memory to **12 GB** (leaving you room to create another VM later if you want, or set it to **4 OCPUs and 24 GB** to use your entire free allocation on this single powerful instance!).
   - **Networking**: Ensure "Create new Virtual Cloud Network (VCN)" is selected, and "Assign a public IPv4 address" is set to **Yes**.
   - **SSH Keys**:
     - Select **Generate a key pair for me**.
     - Click **Save private key** (`.key` file) and **Save public key**. Store them safely on your local computer!
   - **Boot Volume**: Check "Use in-transit encryption" and set the boot volume size to **100 GB** or **150 GB** (within your 200 GB free limit) to give your database plenty of SSD storage.
4. Click **Create** at the bottom. It will take 1-2 minutes for the instance status to change from _Provisioning_ to _Running_. Note the **Public IP Address** of your instance.

---

## Step 3: Configure Cloud Network (VCN) Firewalls

By default, OCI blocks all incoming traffic except SSH (Port 22). We must allow HTTP (80) and HTTPS (443) traffic.

1. On your Instance Details page, click on your **Virtual Cloud Network** (under Primary VNIC section).
2. Under **Resources** (left sidebar), click **Security Lists**.
3. Click the **Default Security List** for your VCN.
4. Click **Add Ingress Rules**.
5. Add the following rules:

#### Rule for HTTP (Port 80)

- **Source Type**: `CIDR`
- **Source CIDR**: `0.0.0.0/0`
- **IP Protocol**: `TCP`
- **Source Port Range**: `All` (leave blank)
- **Destination Port Range**: `80`
- **Description**: `Allow HTTP traffic`
- Click **Add Ingress Rules**.

#### Rule for HTTPS (Port 443)

- **Source Type**: `CIDR`
- **Source CIDR**: `0.0.0.0/0`
- **IP Protocol**: `TCP`
- **Source Port Range**: `All` (leave blank)
- **Destination Port Range**: `443`
- **Description**: `Allow HTTPS traffic`
- Click **Add Ingress Rules**.

---

## Step 4: Connect to Your VM and Configure OS Firewalls

Even though we opened port 80 and 443 in the OCI dashboard, **Ubuntu VMs on Oracle Cloud have an OS-level firewall (iptables) that blocks them by default**. We must disable or update this.

1. Open your terminal (or Command Prompt / PowerShell on Windows) and SSH into your VM:
   ```bash
   ssh -i /path/to/your/ssh_key.key ubuntu@<YOUR_VM_PUBLIC_IP>
   ```
2. Once connected, run the following commands to update and clear OS firewalls:

   ```bash
   # Update system package lists
   sudo apt update && sudo apt upgrade -y

   # Install Docker and Docker Compose
   sudo apt install -y docker.io docker-compose git

   # Allow Docker to run without sudo (optional but recommended)
   sudo usermod -aG docker ubuntu

   # Open Ports 80 and 443 in IPTables (Oracle's default blocker)
   sudo iptables -I INPUT 6 -p tcp --dport 80 -j ACCEPT
   sudo iptables -I INPUT 6 -p tcp --dport 443 -j ACCEPT

   # Save iptables changes so they persist after reboot
   sudo apt-get install iptables-persistent -y
   sudo netfilter-persistent save
   ```

3. Close and reconnect to your SSH session to apply the `docker` group changes:
   ```bash
   exit
   ```

---

## Step 5: Prepare the Django Project for Production

To make your Django app deployable via Docker-Compose in a secure production mode, update your configurations.

### 1. Production Settings Configuration

Ensure your `storefront/settings/prod.py` is configured to use environment variables for keys and database configs, and uses Redis for Caching and Celery.

Create or update `storefront/settings/prod.py` to match this secure setup:

```python
import os
import dj_database_url  # Optional, but environment variables are standard
from storefront.settings.common import *

DEBUG = False

SECRET_KEY = os.environ.get('SECRET_KEY')

# Add your domain name or public IP here
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '').split(',')

# Security Headers for SSL
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Persist Static/Media via Nginx
STATIC_ROOT = os.path.join(BASE_DIR, 'static')
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Production Database (MySQL)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.environ.get('MYSQL_DATABASE', 'storefront3'),
        'HOST': os.environ.get('MYSQL_HOST', 'db'),
        'USER': os.environ.get('MYSQL_USER', 'root'),
        'PASSWORD': os.environ.get('MYSQL_PASSWORD'),
        'PORT': '3306',
        'OPTIONS': {
            'charset': 'utf8mb4',
        }
    }
}

# Production Cache (Redis Container)
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": os.environ.get('REDIS_URL', 'redis://redis:6379/2'),
        'TIMEOUT': 10 * 60,
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    }
}

# Production Celery
CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL', 'redis://redis:6379/1')
```

---

## Step 6: Production-Ready Docker & Docker-Compose Setup

Using Docker-Compose is the single best way to ensure everything starts on boot, dependencies are correctly linked, and data is persisted on your local volume.

In the root of your project directory, create the following 3 files:

### 1. `Dockerfile` (Production)

```dockerfile
FROM python:3.9-slim

# Prevent Python from writing .pyc files & buffering stdout/stderr
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

# Install system dependencies required for mysqlclient and wait-for-it
RUN apt-get update && apt-get install -y \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    netcat-openbsd \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
RUN pip install --no-cache-dir pipenv
COPY Pipfile Pipfile.lock /app/
RUN pipenv install --system --deploy

# Copy project files
COPY . /app/

# Add execution permissions to entrypoint script
RUN chmod +x /app/entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["/app/entrypoint.sh"]
```

### 2. `entrypoint.sh`

This script ensures the MySQL database is up and fully listening before Django attempts migrations.

```bash
#!/bin/sh

echo "Waiting for MySQL database..."
while ! nc -z $MYSQL_HOST 3306; do
  sleep 0.5
done
echo "MySQL started!"

# Run migrations
python manage.py migrate --noinput

# Collect static files
python manage.py collectstatic --noinput

# Start Gunicorn server
exec gunicorn storefront.wsgi:application --bind 0.0.0.0:8000 --workers 3
```

### 3. `nginx.conf`

This configures Nginx as a reverse proxy, manages SSL, and serves static/media files directly.

```nginx
upstream storefront_app {
    server web:8000;
}

server {
    listen 80;
    server_name _;

    # Certbot renewal path
    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }

    location / {
        return 301 https://$host$request_uri;
    }
}

server {
    listen 443 ssl;
    server_name _;

    # SSL Certificates (managed by Certbot)
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    client_max_body_size 20M;

    # Static Files
    location /static/ {
        alias /app/static/;
    }

    # Media Files
    location /media/ {
        alias /app/media/;
    }

    # API and Admin requests
    location / {
        proxy_pass http://storefront_app;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-Proto https;
        proxy_redirect off;
    }
}
```

### 4. `docker-compose.yml` (Production Orchestration)

```yaml
version: "3.8"

services:
  db:
    image: mysql:8.0
    restart: always
    environment:
      MYSQL_DATABASE: storefront3
      MYSQL_ROOT_PASSWORD: secure_root_password_change_me
    volumes:
      - mysql_data:/var/lib/mysql
    expose:
      - "3306"

  redis:
    image: redis:7-alpine
    restart: always
    volumes:
      - redis_data:/data
    expose:
      - "6379"

  web:
    build: .
    restart: always
    environment:
      - DJANGO_SETTINGS_MODULE=storefront.settings.prod
      - SECRET_KEY=your_super_secret_production_key_change_me
      - ALLOWED_HOSTS=yourdomain.com,your_vm_public_ip
      - MYSQL_HOST=db
      - MYSQL_PASSWORD=secure_root_password_change_me
      - REDIS_URL=redis://redis:6379/2
      - CELERY_BROKER_URL=redis://redis:6379/1
    volumes:
      - static_volume:/app/static
      - media_volume:/app/media
    depends_on:
      - db
      - redis

  celery_worker:
    build: .
    restart: always
    command: celery -A storefront worker --loglevel=info
    environment:
      - DJANGO_SETTINGS_MODULE=storefront.settings.prod
      - SECRET_KEY=your_super_secret_production_key_change_me
      - MYSQL_HOST=db
      - MYSQL_PASSWORD=secure_root_password_change_me
      - CELERY_BROKER_URL=redis://redis:6379/1
    depends_on:
      - db
      - redis

  celery_beat:
    build: .
    restart: always
    command: celery -A storefront beat --loglevel=info
    environment:
      - DJANGO_SETTINGS_MODULE=storefront.settings.prod
      - SECRET_KEY=your_super_secret_production_key_change_me
      - MYSQL_HOST=db
      - MYSQL_PASSWORD=secure_root_password_change_me
      - CELERY_BROKER_URL=redis://redis:6379/1
    depends_on:
      - db
      - redis

  nginx:
    image: nginx:1.21-alpine
    restart: always
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/conf.d/default.conf:ro
      - static_volume:/app/static
      - media_volume:/app/media
      - certbot_etc:/etc/letsencrypt
      - certbot_www:/var/www/certbot
    depends_on:
      - web

  certbot:
    image: certbot/certbot
    volumes:
      - certbot_etc:/etc/letsencrypt
      - certbot_www:/var/www/certbot
    entrypoint: "/bin/sh -c 'trap exit TERM; while :; do certbot renew; sleep 12h & wait $${!}; done'"

volumes:
  mysql_data:
  redis_data:
  static_volume:
  media_volume:
  certbot_etc:
  certbot_www:
```

---

## Step 7: Deploy and Set Up Let's Encrypt SSL

1. **Commit and push** your code to your private GitHub/GitLab repository.
2. **Log into your OCI VM via SSH**, and clone your repository:
   ```bash
   git clone <YOUR_GIT_REPOSITORY_URL> storefront
   cd storefront
   ```
3. Create the required configuration files on the VM (`Dockerfile`, `entrypoint.sh`, `nginx.conf`, `docker-compose.yml`) if you haven't committed them, or edit them to add your real production values.

### Point Your Domain Name to the VM Public IP

Go to your Domain Registrar (Namecheap, GoDaddy, Cloudflare, etc.) and add an **A Record**:

- **Type**: `A`
- **Name**: `@` (and `www` if needed)
- **Value**: `<YOUR_VM_PUBLIC_IP>`

### Request SSL Certificate

On your OCI VM:

1. Temporarily comment out port `443` and SSL configuration sections from your `nginx.conf` (or let Certbot run standalone).
2. Run Certbot once in standalone mode to obtain the initial certificate:
   ```bash
   sudo docker run -it --rm --name certbot \
     -v "certbot_etc:/etc/letsencrypt" \
     -v "certbot_www:/var/www/certbot" \
     -p 80:80 certbot/certbot certonly \
     --standalone \
     -d yourdomain.com -d www.yourdomain.com
   ```
3. Certbot will ask for your email and agreement to terms. It will then verify your domain ownership and generate the key and certificate in `/etc/letsencrypt/live/yourdomain.com/`.
4. Restore your production `nginx.conf` (making sure your domain name is correct in it).
5. Start your production containers:
   ```bash
   docker-compose up -d --build
   ```
   _Your site is now live with automated Let's Encrypt renewal checks running every 12 hours!_

---

## Step 8: Prevent Oracle VM Reclamation (Crucial!)

Oracle Cloud has a strict policy: **Always Free Compute instances that are idle may be reclaimed (deleted) by Oracle**.

An instance is considered "idle" if during a 7-day window:

- CPU utilization is less than 15% (for ARM VMs)
- Network utilization is less than 15%
- Memory utilization is less than 15%

Since your initial backend storefront might not have constant traffic, you must prevent Oracle from thinking your instance is idle. The absolute simplest, safe way to prevent this is by running a scheduled script that keeps your CPU/RAM usage safely above 15-20%.

We can install a lightweight utility called `lookbusy` or run a simple cronjob script:

### The Safe Keep-Alive Script

Run this script on your VM to generate a steady ~18% CPU load so Oracle never reclaims it:

1. Create a keep-alive script:
   ```bash
   nano ~/keep_alive.sh
   ```
2. Paste the following bash code:
   ```bash
   #!/bin/bash
   # Run a background loop to consume ~18% CPU on multiple cores for 24/7 activity
   while true; do
       # This causes moderate CPU cycles, pauses, and keeps memory active.
       dd if=/dev/urandom of=/dev/null bs=1M count=1024 2>/dev/null
       sleep 0.8
   done
   ```
3. Make it executable:
   ```bash
   chmod +x ~/keep_alive.sh
   ```
4. Set it to run in the background on startup:
   ```bash
   crontab -e
   ```
   Add this line at the bottom:
   ```text
   @reboot /home/ubuntu/keep_alive.sh > /dev/null 2>&1 &
   ```
5. Trigger it now:
   ```bash
   nohup /home/ubuntu/keep_alive.sh > /dev/null 2>&1 &
   ```

---

## Backup & Maintenance

Because your database is self-hosted on your OCI VM Standard block volume:

- **No Auto-deletions**: Oracle does not wipe block volumes on active VMs.
- **Security Updates**: Ubuntu handles unattended security upgrades by default, keeping your host OS secure.
- **How to Back up Database**:
  Add a cronjob to back up your database every night to Oracle Object Storage (10 GB Free forever) or your GitHub/local computer:
  ```bash
  # Command to dump your MySQL database to an SQL file:
  docker exec storefront_db_1 mysqldump -u root -p'secure_root_password_change_me' storefront3 > backup_$(date +%F).sql
  ```

You now have a fully scalable, enterprise-grade storefront setup (Gunicorn + Nginx HTTPS + Dockerized MySQL + Redis Cache + Redis Celery Queue + Celery Worker & Beat scheduler) running on a massive **24 GB / 4 OCPU ARM instance entirely for free!**
