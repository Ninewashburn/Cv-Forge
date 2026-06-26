CVForge
=======

CVForge est un assistant de candidature local-first qui aide les candidats à
structurer leur parcours professionnel, analyser les offres d'emploi, générer
des documents adaptés sans inventer d'informations et suivre l'historique
complet des candidatures.

Ce dépôt fournit un **squelette** permettant de démarrer rapidement le
développement de ce produit. Il s'articule autour de deux sous-dossiers :

- `backend/` : moteur Python minimal illustrant l'architecture Extract →
  Transform → Validate → Load (ETVL) appliquée aux candidatures.
- `frontend/` : application Angular moderne à utiliser comme base pour
  construire l'interface utilisateur responsive.

Une fois cloné et installé, vous pouvez exécuter le moteur backend sur des
données d'exemple pour observer le pipeline en action.

## Pré-requis

- Python 3.9 ou supérieur
- Node.js
- npm

## Exécution du backend

Depuis le dossier `backend/`, exécutez :

```bash
python -m app.main \
  --profile data/master_profile.sample.json \
  --proofs data/proofs.sample.json \
  --offer data/job_offer.sample.txt \
  --out outputs/result.json
```

Le résultat sera écrit dans `backend/outputs/result.json` et contiendra :

- l'analyse de l'offre ;
- les correspondances et compétences manquantes ;
- la variante de CV générée avec les phrases et leurs sources ;
- des avertissements éventuels.

## API locale de veille candidature

Depuis le dossier `backend/`, lancez :

```bash
uvicorn app.api:app --host 127.0.0.1 --port 8000
```

L'extension navigateur pourra envoyer les métadonnées d'une offre vers
`POST /api/bookmarks`, ou une ressource plus générale vers
`POST /api/watch-items`. Les contrats sont documentés dans
`docs/job_bookmarks.md` et `docs/watch_center.md`.

## Exécution du frontend

Depuis le dossier `frontend/`, installez les dépendances puis lancez Angular :

```bash
npm install
npm start
```

Le frontend utilise le style Angular récent : application standalone, racine
`App`, fichiers `app.ts`, `app.html`, `app.css`, et pas de suffixe
`component` dans les noms de fichiers.

## Structure du projet

- `backend/app/` : code source du moteur (models, parsers, matching,
  génération et validation).
- `backend/data/` : exemples de données (profil, preuves, offre).
- `backend/tests/` : tests unitaires de base.
- `frontend/` : base pour l'application Angular.
- `docs/` : documents de conception et de périmètre.
- `skills.md` : rappel des règles et objectifs pour guider le
  développement.

## Prochaines étapes

1. **Étendre la logique de parsing et de matching** pour prendre en compte
   différents métiers et langages.
2. **Introduire une base de données** (SQLite) pour stocker profils, preuves,
   offres et candidatures.
3. **Exposer une API REST** avec FastAPI pour connecter le frontend.
4. **Développer l'interface Angular** afin que les utilisateurs puissent gérer
   leurs profils, importer des offres et générer leurs documents.
5. **Intégrer l'IA locale** (Ollama) pour affiner l'analyse et proposer des
   reformulations contrôlées.
6. **Ajouter un suivi de candidature** pour gérer les postulations et les
   relances.
