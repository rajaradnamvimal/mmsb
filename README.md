# Twitter Klon Anleitung und Dokumentation

## Installation

```bash
git clone git@github.com:rajaradnamv/twitter-dupe.git
cd twitter-dupe
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Starten

### Datenbank starten
```bash
docker run --name twitter-dupe-db -e POSTGRES_PASSWORD=test -e POSTGRES_USER=test -e POSTGRES_DB=social_media_db -p 5432:5432 -d postgres
```

### Datenbank vorbereiten und Server starten
```bash
source venv/bin/activate
python3 setup_db.py
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

## Tests ausführen

```bash
source venv/bin/activate
python3 -m unittest
```

## API-Endpunkt mit curl _manuell_ testen

### Ubuntu

```bash
apiUrl="http://localhost:5000"

username="john"
password="test"

credentials="${username}:${password}"
base64AuthInfo=$(echo -n "${credentials}" | base64)

curl -X GET -H "Accept: application/json" -H "Authorization: Basic ${base64AuthInfo}" "${apiUrl}/"
```

### Windows

```bash
$apiUrl = "http://localhost:5000"

$username = "john"
$password = "test"
$base64AuthInfo = [Convert]::ToBase64String([Text.Encoding]::ASCII.GetBytes("${username}:${password}"))

$headers = @{
    "Accept" = "application/json"
    "Authorization" = "Basic $base64AuthInfo"
}

Invoke-RestMethod -Uri "$apiUrl/" -Method Get -Headers $headers
```
