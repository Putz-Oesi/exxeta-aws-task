from datetime import datetime

from flask import Flask, redirect, render_template, request, Response

# Flask-Anwendung initialisieren
app = Flask(__name__)

# Temporäre Speicherung aller Rufbereitschaftseinträge
entries = []


# Berechnet die Gesamtdauer aller gespeicherten Einträge
def calculate_total_duration():
    total_minutes = 0

    # Jeden Eintrag durchlaufen und in Minuten addieren
    for entry in entries:
        total_minutes += entry["hours"] * 60 + entry["minutes"]

    # Minuten wieder in Stunden und Minuten umwandeln
    return total_minutes // 60, total_minutes % 60


# Startseite anzeigen
@app.route("/")
def index():
    # Aktuelle Gesamtdauer berechnen
    total_hours, total_minutes = calculate_total_duration()

    # HTML-Template mit den aktuellen Daten rendern
    return render_template(
        "index.html",
        entries=entries,
        total_hours=total_hours,
        total_minutes=total_minutes,
        error=None,
    )


# Neuen Rufbereitschaftseintrag hinzufügen
@app.route("/add", methods=["POST"])
def add_entry():

    # Formulardaten aus dem Browser auslesen
    start_raw = request.form.get("start", "").strip()
    end_raw = request.form.get("end", "").strip()
    customer = request.form.get("customer", "").strip()
    incident = request.form.get("incident", "").strip()

    total_hours, total_minutes = calculate_total_duration()

    # Serverseitige Prüfung der Pflichtfelder
    if not start_raw or not end_raw or not customer or not incident:
        return render_template(
            "index.html",
            entries=entries,
            total_hours=total_hours,
            total_minutes=total_minutes,
            error="Bitte alle Pflichtfelder ausfüllen.",
        )

    # Datums-Strings in datetime-Objekte umwandeln
    start = datetime.strptime(start_raw, "%Y-%m-%dT%H:%M")
    end = datetime.strptime(end_raw, "%Y-%m-%dT%H:%M")

    # Prüfen, ob die Endzeit nach der Startzeit liegt
    if end <= start:
        return render_template(
            "index.html",
            entries=entries,
            total_hours=total_hours,
            total_minutes=total_minutes,
            error="Die Endzeit muss nach der Startzeit liegen.",
        )

    # Dauer des Einsatzes berechnen
    duration = end - start
    entry_total_minutes = int(duration.total_seconds() / 60)
    hours = entry_total_minutes // 60
    minutes = entry_total_minutes % 60

    # Eintrag als Dictionary erstellen
    entry = {
        "start": start_raw,
        "end": end_raw,
        "customer": customer,
        "incident": incident,
        "hours": hours,
        "minutes": minutes,
    }

    # Eintrag zur temporären Liste hinzufügen
    entries.append(entry)

    # Startseite neu laden
    return redirect("/")


# Eintrag anhand seines Index löschen
@app.route("/delete/<int:index>", methods=["POST"])
def delete_entry(index):
    if 0 <= index < len(entries):
        entries.pop(index)

    # Startseite neu laden
    return redirect("/")


# Health-Endpunkt für Monitoring und Statusprüfungen
@app.route("/health")
def health():
    return Response("OK", status=200, content_type="text/plain")


# Flask Development Server (nur für lokale Entwicklung)
if __name__ == "__main__":
    app.run(debug=True)