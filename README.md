# Rufbereitschaftsrechner

## Projektbeschreibung

Dieses Projekt entstand im Rahmen einer technischen Praxisaufgabe.

Ziel war es, eine kleine Python-Webanwendung zu entwickeln und auf AWS bereitzustellen. Der Rufbereitschaftsrechner erfasst Einsätze mit Kunde, Incidentnummer, Beginn und Ende. Daraus werden die Dauer einzelner Einträge sowie die Gesamtdauer berechnet.

Zusätzlich wurde die benötigte AWS-Infrastruktur aufgebaut. Dazu gehören eine EC2-Instanz, ein privater S3-Bucket, eine IAM-Rolle, ein eigenes VPC, ein öffentliches Subnetz, Nginx, Gunicorn und ein CloudWatch-Alarm.


## Funktionen

Der Rufbereitschaftsrechner bietet folgende Funktionen:

- Erfassung von Rufbereitschaftseinsätzen
- Eingabe von Kunde und Incidentnummer
- Berechnung der Einsatzdauer
- Berechnung der Gesamtdauer aller Einträge
- Löschen einzelner Einträge
- Health-Endpunkt (`/health`) für Statusprüfungen


## Verwendete Technologien

- Python
- Flask
- HTML
- CSS
- Gunicorn
- Nginx
- Amazon EC2
- Amazon S3
- AWS IAM
- AWS Systems Manager
- Amazon CloudWatch


## Architektur

Die Anwendung läuft auf einer EC2-Instanz mit Amazon Linux 2023 und ist über HTTP erreichbar. Für den öffentlichen Zugriff wird Nginx verwendet, der Anfragen auf Port 80 entgegennimmt und intern an Gunicorn weiterleitet. Gunicorn stellt die Flask-Anwendung als WSGI-Server bereit.

Der interne Anwendungsport ist nicht öffentlich freigegeben. Nach außen ist nur Port 80 erreichbar, während der administrative Zugriff auf die Instanz ausschließlich über AWS Systems Manager Session Manager erfolgt.

Das Deployment-Paket liegt in einem privaten S3-Bucket und wird von der EC2-Instanz über ihre IAM-Rolle heruntergeladen. Die dafür erstellte IAM-Policy ist auf den lesenden Zugriff auf genau dieses ZIP-Archiv begrenzt.

Zur Überwachung wurde ein CloudWatch-Alarm für die CPU-Auslastung der EC2-Instanz eingerichtet. Zusätzlich stellt die Flask-Anwendung den Endpunkt `/health` bereit, über den geprüft werden kann, ob die Anwendung erreichbar ist.


## AWS-Infrastruktur

Für die Bereitstellung wurde eine eigene AWS-Umgebung in der Region eu-central-1 aufgebaut. Verwendet wurde ein eigenes VPC mit öffentlichem Subnetz, Internet Gateway und eigener Route Table. Die EC2-Instanz befindet sich in diesem öffentlichen Subnetz und erhält eine öffentliche IPv4-Adresse.

Die Security Group erlaubt eingehende Verbindungen nur auf Port 80. Port 22 ist nicht freigegeben, da der administrative Zugriff ausschließlich über AWS Systems Manager Session Manager erfolgt.

Für den Zugriff auf das Deployment-Paket wurde eine IAM-Rolle mit einer eigenen Policy erstellt. Diese Policy erlaubt nur `s3:GetObject` auf das konkrete ZIP-Archiv im privaten S3-Bucket.


## Deployment

Die Anwendung wird als ZIP-Archiv in einem privaten Amazon S3-Bucket bereitgestellt. Beim Start der EC2-Instanz lädt ein User-Data-Skript das Deployment-Paket herunter und richtet die Anwendung automatisch ein. Dazu gehören unter anderem die Installation der benötigten Abhängigkeiten, die Einrichtung von Gunicorn und Nginx sowie die Erstellung eines systemd-Services.

Nach der ersten Einrichtung wird die Anwendung automatisch gestartet und ist über die öffentliche IP-Adresse der EC2-Instanz erreichbar. Da sie als systemd-Service eingerichtet wurde, startet sie auch nach einem Neustart der Instanz automatisch wieder.


## Projektstruktur

```text
.
├── static/
│   └── style.css
├── templates/
│   └── index.html
├── .gitignore
├── app.py
├── README.md
├── requirements.txt
└── user-data.sh
```


## Statusprüfung

Die Anwendung stellt den Health-Endpunkt `/health` bereit. Dieser gibt bei erfolgreicher Ausführung die Antwort `OK` mit dem HTTP-Statuscode 200 zurück.

Der Endpunkt kann sowohl extern über Port 80 als auch intern auf der EC2-Instanz geprüft werden.