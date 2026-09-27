# JEFAL

> Ta voix. Ton activite. Ton avenir.

JEFAL est un agent vocal pour les petits commercants et acteurs de l'economie informelle. Il permet d'enregistrer et de consulter des operations commerciales a partir de commandes vocales, notamment en wolof.

## Architecture

Voix utilisateur
    |
    v
M-Kiriku ASR
    |
    v
Texte Wolof / Francais
    |
    v
Compréhension de l'intention
    |
    v
Intent + donnees structurees
    |
    v
Validation Pydantic
    |
    v
ActionExecutor
    |
    v
Services metier
    |
    v
PostgreSQL
    |
    v
Resultat
    |
    v
Kiriku TTS
    |
    v
Voix

## Stack

- Python 3.13
- FastAPI
- PostgreSQL 16
- SQLAlchemy
- Alembic
- Pydantic
- M-Kiriku ASR
- Kiriku Wolof TTS

## Prerequis

- Python 3.13
- PostgreSQL 16
- Git
- pyenv
- Python 3.11 pour le service TTS

## Installation

### 1. Cloner le projet

git clone https://github.com/DebugNinja10/jeffal.git
cd jeffal

### 2. Environnement principal

python3.13 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

### 3. Base de donnees

Configurer PostgreSQL puis creer le fichier .env.

Exemple :

DATABASE_URL=postgresql+psycopg://jeffal_user:mot_de_passe@localhost:5432/jeffal_db

### 4. Migrations

alembic upgrade head

## M-Kiriku ASR

JEFAL utilise le modele :

AIHubSN/M-Kiriku-ASR

Le modele ASR est charge automatiquement au demarrage de l'application.

## Kiriku TTS

JEFAL utilise le modele :

AIHubSN/Kiriku-Wolof-TTS

Le fichier model.pth n'est pas versionne dans GitHub en raison de sa taille.

Le dossier local attendu est :

kiriku_tts/
    config.json
    model.pth

Le modele doit etre telecharge depuis le depot officiel du modele et place dans kiriku_tts/.

### Environnement TTS

Le service TTS utilise Python 3.11.

pyenv install 3.11.9
pyenv virtualenv 3.11.9 jeffal-tts
pyenv activate jeffal-tts
pip install TTS==0.19.0

### Lancer le service TTS

python -m uvicorn tts_service.main:app --host 127.0.0.1 --port 8001

Test :

curl http://127.0.0.1:8001/health

Le service doit retourner :

{
  "status": "ok",
  "service": "kiriku-tts"
}

### Test TTS

curl -X POST http://127.0.0.1:8001/tts \
  -H "Content-Type: application/json" \
  -d '{"text":"salamalekum, na nga def"}' \
  --output test_tts.wav

## Lancer JEFAL

Dans un autre terminal :

source .venv/bin/activate
uvicorn app.main:app --reload

API :

http://127.0.0.1:8000

Swagger :

http://127.0.0.1:8000/docs

## Pipeline vocal actuel

Audio
  |
  v
M-Kiriku ASR
  |
  v
Texte
  |
  v
Detection intention
  |
  v
Validation
  |
  v
ActionExecutor
  |
  v
Service metier
  |
  v
PostgreSQL

Exemple :

mun naa ceeb 2 kilos

Le systeme peut transcrire la commande, identifier une vente et enregistrer l'operation correspondante.

## Structure

app/
    agents/
    auth/
    core/
    database/
    models/
    routers/
    schemas/
    services/

tts_service/
    main.py

## Fichiers non versionnes

Les fichiers suivants sont exclus du depot :

- .env
- .venv/
- kiriku_tts/
- fichiers audio de test
- fichiers de sauvegarde
- caches Python

Le modele Kiriku TTS doit donc etre installe separement sur chaque environnement.

## Etat actuel

Le pipeline vocal de JEFAL est fonctionnel :

- authentification
- reception audio
- transcription avec M-Kiriku ASR
- detection d'intention
- execution d'actions metier
- enregistrement PostgreSQL
- synthese vocale avec Kiriku TTS

Le projet continue son evolution vers un agent vocal capable de gerer davantage d'operations commerciales et de comprendre naturellement les langues nationales.
