#!/bin/bash

# Bei einem Fehler das Skript sofort abbrechen
set -e

# Betriebssystem aktualisieren und benötigte Pakete installieren
dnf update -y
dnf install -y python3 python3-pip unzip nginx

# Zielverzeichnis für die Anwendung erstellen
mkdir -p /opt/rufbereitschaftsrechner

# Deployment-ZIP aus dem privaten S3-Bucket herunterladen
aws s3 cp s3://juergen-kienesberger-exxeta-app/application/rufbereitschaftsrechner.zip /tmp/rufbereitschaftsrechner.zip

# Anwendung entpacken
unzip -o /tmp/rufbereitschaftsrechner.zip -d /opt/rufbereitschaftsrechner

# In das Projektverzeichnis wechseln
cd /opt/rufbereitschaftsrechner

# Virtuelle Python-Umgebung erstellen
python3 -m venv venv

# Python-Abhängigkeiten aus der requirements.txt installieren
/opt/rufbereitschaftsrechner/venv/bin/pip install -r requirements.txt

# systemd-Service für Gunicorn erstellen
cat > /etc/systemd/system/rufbereitschaft.service << 'EOF'
[Unit]
Description=Rufbereitschaftsrechner Gunicorn Service
After=network.target

[Service]
User=ec2-user
WorkingDirectory=/opt/rufbereitschaftsrechner
ExecStart=/opt/rufbereitschaftsrechner/venv/bin/gunicorn --bind 127.0.0.1:8000 app:app
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# Nginx als Reverse Proxy konfigurieren
cat > /etc/nginx/conf.d/rufbereitschaft.conf << 'EOF'
server {
    listen 80;
    server_name _;

    location / {
        # Anfragen intern an Gunicorn weiterleiten
        proxy_pass http://127.0.0.1:8000;
    }
}
EOF

# Standardkonfiguration von Nginx entfernen
rm -f /etc/nginx/conf.d/default.conf

# Neue systemd-Konfiguration einlesen
systemctl daemon-reload

# Gunicorn dauerhaft aktivieren und starten
systemctl enable rufbereitschaft
systemctl start rufbereitschaft

# Nginx dauerhaft aktivieren und starten
systemctl enable nginx
systemctl restart nginx