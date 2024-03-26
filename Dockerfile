# Eine offizielle Python-Laufzeitumgebung als uebergeordnetes Bild verwenden
FROM python:3.10-slim-buster
RUN apt-get update -y
RUN apt-get install -y python3-pip

ENV PYTHONBUFFERED True

# Setzen Sie das Arbeitsverzeichnis im Container auf /app
WORKDIR /app

# Hinzufuegen des Inhalts des aktuellen Verzeichnisses in den Container unter /app
ADD . /app

# Installieren Sie alle benoetigten Pakete, die in requirements.txt angegeben sind.
RUN pip install --no-cache-dir -r requirements.txt

# Port 5000 fuer die Welt ausserhalb dieses Containers verfuegbar machen
EXPOSE 5000

# app.py beim Starten des Containers ausfuehren
CMD ["python", "setup_db.py"]
CMD ["python", "app.py"]
