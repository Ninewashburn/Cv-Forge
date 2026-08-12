# CVForge

**Adapter son CV à une offre sans jamais rien inventer.**

CVForge est un outil de candidature **local-first** : il analyse une offre d'emploi, mesure ce
que ton CV couvre déjà, t'aide à l'adapter — à la main ou avec l'IA de *ton* choix — et met
chaque changement en évidence dans un « Avant / Après » où rien ne part à l'export sans ta
validation. L'idée en une phrase : **tout ce qui est sur ton CV, tu peux le prouver en
entretien.**

## Trois questions avant tout

- **Mes données partent-elles quelque part ?** — **Jamais.** Pas de cloud, pas de compte, pas
  de télémétrie, pas de tracker. Tout tourne et reste sur ta machine.
- **Faut-il une connexion internet ?** — **Non**, sauf si *toi* tu choisis d'utiliser une IA
  (ton chat habituel par copier-coller, ou ta propre clé API).
- **Faut-il installer quelque chose ?** — Python (et Node pour construire l'interface), voir
  Démarrage. Pour essayer sans rien installer :
  [`prototypes/cvforge-lite/index.html`](prototypes/cvforge-lite/index.html), un simple fichier
  HTML à ouvrir dans le navigateur.

## Ce que fait la V1

Un parcours guidé en cinq étapes :

1. **Sources** — colle (ou importe en PDF/TXT, extraction 100 % locale) l'offre, ton CV, et en
   option ton profil LinkedIn — jamais exporté, il sert seulement à révéler ce que ton CV oublie.
2. **Analyse** — matching par mots-clés, **sans IA** : ce que ton CV couvre, ce que LinkedIn
   révèle, ce qui manque vraiment. Double score CV / potentiel.
3. **Adaptation** — trois niveaux, tous optionnels au-delà du premier :
   - **Manuelle** : édition côte à côte, score recalculé en direct à chaque pause de frappe.
   - **Copilote** (recommandé) : CVForge prépare un prompt verrouillé anti-hallucination, tu le
     colles dans *ton* ChatGPT ou Claude, tu rapportes la réponse. Zéro clé, zéro coût.
   - **Clé API** (avancé) : appel direct à Anthropic avec ta clé — consentement explicite qui
     affiche exactement ce qui part. La clé est stockée localement côté application, jamais
     exposée au navigateur, jamais incluse dans les backups.
4. **Avant / Après** — chaque passage ajouté doit être confirmé « vrai et prouvable » ; tant que
   tout n'est pas validé, l'export reste verrouillé.
5. **Export & suivi** — PDF prêt à envoyer + micro-suivi de candidature (envoyée ? réponse ?
   entretien ?) en trois clics.

À côté du parcours : un **profil maître** et une **banque de preuves** (faits reliés à leurs
preuves — note, lien, document avec pièce jointe) — la matière première dont l'IA n'a pas le
droit de sortir.

**Principe non négociable :** l'IA reformule, réorganise et priorise du contenu existant — elle
n'invente jamais un fait, un chiffre ou une compétence. Chaque appel embarque ces règles dans le
prompt, et aucune proposition n'est appliquée sans passer par l'Avant / Après.

## Démarrage

Pré-requis : **Python 3.12+** (et **Node.js 20+** pour construire l'interface ; sans Node,
l'application démarre en mode API seule sur `/docs`).

**En un double-clic** — `start.bat` (Windows) ou `./start.sh` (macOS/Linux) : la première
exécution crée l'environnement Python, construit l'interface si `frontend/node_modules` est
présent, puis ouvre <http://localhost:8000>.

**En mode développement** :

```bash
# Terminal 1 — API sur :8000
cd backend
python -m venv .venv
source .venv/bin/activate            # Windows : .venv\Scripts\activate
pip install -e ".[dev]"
uvicorn app.main:app --port 8000

# Terminal 2 — interface sur :4200 (proxy vers :8000)
cd frontend
npm install && npm start
```

**Construire l'exe portable** (Windows, un seul binaire double-cliquable — Python + FastAPI +
interface, aucune installation) :

```bash
cd backend
python build_portable.py     # construit l'interface au besoin, puis gèle avec PyInstaller
# → backend/dist/CVForge.exe
```

Au lancement, l'exe ouvre une **fenêtre native** (WebView2, present par defaut sur Windows 11) ;
si elle n'est pas disponible, il se rabat automatiquement sur ton **navigateur** par defaut. Rien
a installer dans les deux cas.

Par défaut, l'exe range les données dans `~/.cvforge/`. Pour un **mode clé USB** (données à côté
de l'exe, dans `./data/`), pose un fichier vide nommé `cvforge.portable` à côté du binaire.

## Où sont mes données ?

Dans `~/.cvforge/` (une base SQLite + les pièces jointes de preuves), sous ton contrôle total :

- **Exporter** : bouton « Exporter mes données (ZIP) » sur l'accueil — base + fichiers, complet.
- **Restaurer** : le même ZIP, sur n'importe quelle machine.
- Ta clé API n'est **jamais** incluse dans ces archives, ni écrasée par une restauration.

## Architecture

Monorepo : [`backend/`](backend/) (FastAPI, SQLAlchemy, SQLite, migrations Alembic) et
[`frontend/`](frontend/) (Angular 21 — standalone, signals, zoneless). En usage réel, un seul
process : FastAPI sert le build Angular sur `localhost:8000`. Le schéma de données est
sync-ready dès la V1 (UUID, timestamps UTC, soft delete) pour préparer la suite sans migration
douloureuse.

## Qualité

```bash
# backend (venv activé)
pytest                    # 81 tests
ruff check app tests

# frontend
npm run lint
npm run lint:tells        # garde anti-tells IA (frontend, prototypes, backend)
npx prettier --check src
```

Un **hook pre-commit** rejoue `lint:tells` et bloque le commit si un tell IA passe. Active-le
une fois par clone : `node frontend/scripts/setup-hooks.mjs` (pose `core.hooksPath` sur
`.githooks/`).

## Statut & feuille de route

**V1 fonctionnelle** : le parcours complet (offre → analyse → adaptation → Avant/Après → PDF →
suivi) marche de bout en bout, avec 81 tests backend. Elle n'a pas encore été éprouvée par de
vrais testeurs — les retours sont bienvenus via les issues.

Feuille de route détaillée : [`docs/roadmap/ROADMAP.md`](docs/roadmap/ROADMAP.md) — V1.5 : exe
portable (clé USB), linter de CV ; V2 : suivi de candidatures enrichi ; V3 : IA 100 % locale
(Ollama).

## Licence

[MIT](LICENSE).
