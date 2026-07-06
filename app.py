from datetime import datetime

from flask import Flask, redirect, render_template, request, Response

app = Flask(__name__)

entries = []


def calculate_total_duration():
    total_minutes = 0

    for entry in entries:
        total_minutes += entry["hours"] * 60 + entry["minutes"]

    return total_minutes // 60, total_minutes % 60


@app.route("/")
def index():
    total_hours, total_minutes = calculate_total_duration()

    return render_template(
        "index.html",
        entries=entries,
        total_hours=total_hours,
        total_minutes=total_minutes,
        error=None,
    )


@app.route("/add", methods=["POST"])
def add_entry():
    start_raw = request.form.get("start", "").strip()
    end_raw = request.form.get("end", "").strip()
    customer = request.form.get("customer", "").strip()
    incident = request.form.get("incident", "").strip()

    total_hours, total_minutes = calculate_total_duration()

    if not start_raw or not end_raw or not customer or not incident:
        return render_template(
            "index.html",
            entries=entries,
            total_hours=total_hours,
            total_minutes=total_minutes,
            error="Bitte alle Pflichtfelder ausfüllen.",
        )

    start = datetime.strptime(start_raw, "%Y-%m-%dT%H:%M")
    end = datetime.strptime(end_raw, "%Y-%m-%dT%H:%M")

    if end <= start:
        return render_template(
            "index.html",
            entries=entries,
            total_hours=total_hours,
            total_minutes=total_minutes,
            error="Die Endzeit muss nach der Startzeit liegen.",
        )

    duration = end - start
    entry_total_minutes = int(duration.total_seconds() / 60)
    hours = entry_total_minutes // 60
    minutes = entry_total_minutes % 60

    entry = {
        "start": start_raw,
        "end": end_raw,
        "customer": customer,
        "incident": incident,
        "hours": hours,
        "minutes": minutes,
    }

    entries.append(entry)

    return redirect("/")


@app.route("/delete/<int:index>", methods=["POST"])
def delete_entry(index):
    if 0 <= index < len(entries):
        entries.pop(index)

    return redirect("/")


@app.route("/health")
def health():
    return Response("OK", status=200, content_type="text/plain")


if __name__ == "__main__":
    app.run(debug=True)