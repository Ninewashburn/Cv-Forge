CVForge Backend
================

Ce dossier contient le backend de CVForge, un assistant local-first de
candidature conçu pour analyser des offres d'emploi, comparer avec un profil
professionnel structuré et générer une candidature adaptée sans inventer
d'informations.

Structure
---------

- `app/` : contient le code source du backend, organisé en modules distincts :
  - `models.py` : définitions des dataclasses pour représenter des faits, des
    preuves et d'autres entités.
  - `offer_parser.py` : parseur simple d'offres d'emploi.
  - `matching_engine.py` : logique de comparaison entre les faits et une offre.
  - `generation_engine.py` : générateur d'une variante de CV basée sur les
    correspondances.
  - `validation_engine.py` : vérifie que les sorties ne violent pas les règles
    anti-hallucination.
  - `main.py` : point d'entrée en ligne de commande.
- `data/` : contient des exemples de fichiers JSON pour un profil maître, des
  preuves associées et une offre d'emploi.
- `tests/` : contient des tests unitaires simples.

Installation de test
--------------------

```bash
python -m pip install -e ".[dev]"
python -m pytest
```

API locale
----------

```bash
uvicorn app.api:app --host 127.0.0.1 --port 8000
```

L'endpoint `POST /api/bookmarks` reçoit les offres envoyées par l'extension
navigateur sous forme de métadonnées minimales : URL, titre, entreprise, source,
date de capture et statut. L'endpoint `POST /api/watch-items` généralise cette
logique aux formations, news, événements et candidatures.

Usage
-----

Pour exécuter le moteur sur les exemples fournis :

```bash
python -m app.main \
  --profile data/master_profile.sample.json \
  --proofs data/proofs.sample.json \
  --offer data/job_offer.sample.txt \
  --out outputs/result.json
```

Ceci génère un fichier `outputs/result.json` contenant l'analyse de l'offre,
les correspondances, la variante de CV et les avertissements.

Prochaines étapes
-----------------

- Améliorer l'extraction d'informations des offres (NLP, support multilingue).
- Ajouter un modèle de données persistant (SQLite, ORM).
- Exposer une API REST avec FastAPI.
- Connecter le frontend Angular ou une PWA.
