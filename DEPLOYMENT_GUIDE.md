# Deployment and Local Development Guide

This guide provides detailed instructions for deploying the AI-Powered Restaurant Booking Management System both to your own server and for local development.

## Required Python Dependencies

When setting up this project locally, you'll need to install the following Python packages:

```
elevenlabs>=0.2.24
email-validator>=2.0.0
flask>=2.3.0
flask-sqlalchemy>=3.0.0
gunicorn>=20.1.0
openai>=1.0.0
psycopg2-binary>=2.9.0
pydub>=0.25.0
python-dotenv>=1.0.0
requests>=2.30.0
sqlalchemy>=2.0.0
twilio>=8.0.0
Werkzeug>=2.3.0
```

You can install these using pip:

```bash
pip install elevenlabs email-validator flask flask-sqlalchemy gunicorn openai psycopg2-binary pydub python-dotenv requests sqlalchemy twilio Werkzeug
```

## Local Development Setup

### Setting up the Database

1. Install PostgreSQL on your system if you haven't already
2. Create a new database for the application:

```bash
psql -U postgres
CREATE DATABASE restaurant_db;
```

3. Update your .env file with the database connection string:

```
DATABASE_URL=postgresql://username:password@localhost:5432/restaurant_db
```

### Running the Application Locally

1. Ensure you've set up all environment variables as outlined in the README.md
2. Start the Flask development server:

```bash
# For development
export FLASK_APP=main.py
export FLASK_ENV=development
flask run

# For production-like environment
gunicorn --bind 0.0.0.0:5000 --workers 4 main:app
```

## Deploying to a VPS (Virtual Private Server)

### Server Preparation

1. Set up a server with Ubuntu or your preferred Linux distribution
2. Install required software:

```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv postgresql nginx
```

### Application Setup

1. Clone your repository to the server:

```bash
git clone <repository-url>
cd restaurant-booking-system
```

2. Create and activate a virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate
```

3. Install dependencies:

```bash
pip install elevenlabs email-validator flask flask-sqlalchemy gunicorn openai psycopg2-binary pydub python-dotenv requests sqlalchemy twilio Werkzeug
```

4. Set up environment variables:
   - Create a .env file in the application root with all required variables
   - Alternatively, set them up in your systemd service file

### Database Setup

1. Create a PostgreSQL database:

```bash
sudo -u postgres psql
CREATE DATABASE restaurant_db;
CREATE USER myuser WITH PASSWORD 'mypassword';
GRANT ALL PRIVILEGES ON DATABASE restaurant_db TO myuser;
```

2. Update your .env file with the correct database URL

### Setting up Nginx as a Reverse Proxy

1. Create an Nginx site configuration:

```bash
sudo nano /etc/nginx/sites-available/restaurant-booking
```

2. Add the following configuration:

```
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

3. Enable the site:

```bash
sudo ln -s /etc/nginx/sites-available/restaurant-booking /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### Setting up SSL with Let's Encrypt

1. Install Certbot:

```bash
sudo apt install certbot python3-certbot-nginx
```

2. Obtain and configure SSL certificate:

```bash
sudo certbot --nginx -d your-domain.com
```

### Creating a Systemd Service

1. Create a service file:

```bash
sudo nano /etc/systemd/system/restaurant-booking.service
```

2. Add the following configuration:

```
[Unit]
Description=Restaurant Booking System
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/path/to/restaurant-booking-system
Environment="PATH=/path/to/restaurant-booking-system/venv/bin"
EnvironmentFile=/path/to/restaurant-booking-system/.env
ExecStart=/path/to/restaurant-booking-system/venv/bin/gunicorn --workers 4 --bind 0.0.0.0:5000 main:app
Restart=always

[Install]
WantedBy=multi-user.target
```

3. Enable and start the service:

```bash
sudo systemctl enable restaurant-booking
sudo systemctl start restaurant-booking
```

## Twilio Configuration for Production

For your production deployment, update your Twilio webhook URL to point to your actual domain:

```
https://your-domain.com/twilio/incoming-call
```

Make sure your server is accessible from the internet and that your domain is properly set up with DNS.

## Monitoring and Maintenance

### View Logs

```bash
# View application logs
sudo journalctl -u restaurant-booking.service

# View Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

### Update the Application

1. Pull the latest code:

```bash
cd /path/to/restaurant-booking-system
git pull
```

2. Restart the service:

```bash
sudo systemctl restart restaurant-booking
```

### Database Backups

Set up regular database backups:

```bash
# Create a backup script
sudo nano /usr/local/bin/backup-db.sh
```

Add the following content:

```bash
#!/bin/bash
DATE=$(date +%Y-%m-%d_%H-%M-%S)
BACKUP_DIR="/path/to/backups"
pg_dump -U postgres restaurant_db > $BACKUP_DIR/restaurant_db_$DATE.sql
```

Make it executable and set up a cron job:

```bash
sudo chmod +x /usr/local/bin/backup-db.sh
sudo crontab -e
```

Add the following line to run daily backups at 2 AM:

```
0 2 * * * /usr/local/bin/backup-db.sh
```

## Troubleshooting Common Issues

### Application Not Starting

1. Check if gunicorn is running:

```bash
ps aux | grep gunicorn
```

2. Check the application logs:

```bash
sudo journalctl -u restaurant-booking.service
```

### Database Connectivity Issues

1. Ensure PostgreSQL is running:

```bash
sudo systemctl status postgresql
```

2. Check database connection:

```bash
psql -U myuser -d restaurant_db -h localhost -p 5432
```

### Twilio Webhook Issues

1. Ensure your domain is accessible from the internet
2. Verify your Twilio webhook URL is correct
3. Check Nginx logs for incoming requests
4. Test the webhook endpoint with tools like Postman