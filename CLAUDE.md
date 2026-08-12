# CLAUDE.md — CVForge

Outil **local-first** de candidature basée sur des preuves. Lire `ROADMAP.md` avant toute feature.

---

## RÈGLE #1 — Périmètre de build

- Construire **UNIQUEMENT** la section V1 de `ROADMAP.md`.
- Les maquettes d'interface = vision cible V3+ (North Star). **Ne pas les implémenter.**
- Interface V1 = parcours linéaire guidé (wizard), **pas** l'Atelier 3 colonnes des maquettes.
- Toute idée hors V1 → proposer un ajout dans `ROADMAP.md` (V2+). Ne jamais coder directement.

---

## Architecture

- Monorepo : `backend/` (FastAPI) + `frontend/` (Angular)
- **V1 = web app locale** : un seul process — FastAPI sert le build Angular (StaticFiles) sur `localhost:8000`. Pas d'Electron/Tauri en V1.
- Dev : `ng serve` (4200) + uvicorn (8000), proxy Angular vers l'API.
- Lancement utilisateur : script double-cliquable (`start.bat` / `start.sh`) qui démarre uvicorn et ouvre le navigateur.
- SQLite : **jamais de chemin en dur**. Tout accès passe par une fonction unique `resolve_data_dir()` (centralisée, jamais contournée). En V1 elle retourne simplement le dossier utilisateur (`~/.cvforge/` via `platformdirs`). La logique portable s'ajoutera en V1.5 dans cette seule fonction, sans toucher au reste du code.
  - Ordre de résolution (cible V1.5, à câbler dès V1 même si seul le dernier niveau est actif) : 1) variable d'env `CVFORGE_DATA` → 2) marqueur `cvforge.portable` à côté de l'exe → données dans `./data/` (mode clé USB) → 3) défaut `~/.cvforge/`.
  - Principe : local-first = données sous contrôle total de l'utilisateur, **pas** forcément collées à l'app. `~/.cvforge/` respecte le principe autant que la clé USB. La portabilité est une option, pas le défaut.

## Schéma de données — NON NÉGOCIABLE (sync cloud V3 anticipée)

- Clés primaires : **UUID v4**. Jamais d'auto-increment.
- `created_at` / `updated_at` sur toutes les tables.
- **Soft delete** (`deleted_at`) — jamais de DELETE physique.
- Migrations Alembic dès la première table.

## Backend — FastAPI / Python 3.12

- Pydantic v2 pour tous les schémas I/O. Type hints partout.
- Logique métier dans des **services**, jamais dans les route handlers.
- SQLAlchemy 2.x. Tests : pytest.
- **Aucun appel réseau sortant**, sauf un appel LLM explicitement déclenché par l'utilisateur (avec sa propre clé API).

## Frontend — Angular 21+

- Standalone components, Signals, OnPush, `inject()`, `takeUntilDestroyed`.
- TypeScript strict. `any` interdit (`unknown` si nécessaire).
- Lazy loading des routes. Structure `core/` `shared/` `features/` `layout/`.
- **Diff Viewer = composant central** : avant/après côte à côte, surlignage des modifications. Lisible par un non-dev — pas un diff git.
  - **Terminologie UI — NON NÉGOCIABLE** : dans toute l'interface et les textes vus par l'utilisateur, on dit **« Avant / Après »**, jamais **« Diff »** (jargon dev qui sonne faux en français — on dit « la différence », pas « le diff »). « Diff Viewer » reste uniquement le **nom interne** du composant/code (classes, fonctions). Cf. règle « zéro jargon tech dans l'UI ».

---

## Principes produit → contraintes de code

1. **Anti-hallucination** : l'IA reformule / réorganise / priorise uniquement du contenu existant (profil maître + banque de preuves). Le prompt système de chaque appel LLM doit l'imposer explicitement. Toute suggestion IA est affichée comme **proposition à valider** — jamais appliquée silencieusement.
2. **IA optionnelle** : chaque feature V1 fonctionne sans LLM. Le matching mots-clés = fréquence / string matching, pas d'IA.
3. **Privacy** : avant tout appel LLM, consentement explicite + affichage de **ce qui est envoyé** (CV + offre partent chez le fournisseur). Aucune télémétrie, aucun tracking, aucun compte. Formulation UI de référence : « Vos données restent locales par défaut. Rien n'est partagé sans votre accord. »
4. **Données utilisateur** : export/import ZIP complet (SQLite + fichiers de preuves) — fonctionnel dès la V1.

---

## Branchement IA — 3 niveaux en V1

- **Niveau 0 — Sans IA** : matching mots-clés + adaptation manuelle. Le produit complet fonctionne ainsi.
- **Niveau 1 — Mode copilote (défaut tout public)** : bouton « Préparer le prompt » → CVForge génère un prompt verrouillé (instructions anti-hallucination + profil maître + offre) → copie dans le presse-papier → ouvre claude.ai / chatgpt.com dans un **nouvel onglet** → l'utilisateur colle la réponse dans CVForge → passage **obligatoire** par le Diff Viewer.
  - **Jamais d'iframe** : claude.ai et chatgpt.com bloquent l'embarquement (X-Frame-Options / CSP `frame-ancestors`). Webview dockée envisageable en V1.5 (Tauri), en mode passif uniquement.
  - **Jamais d'automatisation** des sites des fournisseurs (injection de prompt, scraping de réponse) — violation de ToS, fragile.
- **Niveau 2 — Clé API utilisateur** : intégration directe, prompt système anti-hallucination imposé, réponse injectée dans le Diff Viewer.
- **Niveau 3 — Ollama** : V3, **ne pas coder en V1**. Installation guidée avec consentement (taille du téléchargement, RAM requise).

Note privacy à afficher à l'utilisateur : les données envoyées via **API** ne servent pas à l'entraînement des modèles ; ce qui est collé dans le **chat grand public** peut y servir selon les réglages du compte. CVForge informe, l'utilisateur choisit.

---

## Interdits

- Toute feature V1.5+ : ATS checker, versioning, DOCX, suivi multi-statuts, dashboard, extension, mobile, Ollama, sync, i18n, simulateur d'entretien, pitch audio.
- `localStorage` / `sessionStorage` pour les données métier — tout passe par l'API → SQLite.
- Secrets en dur. La clé API LLM est saisie par l'utilisateur, stockée côté backend dans le dossier utilisateur, jamais exposée au frontend ni committée.
- `console.log` en production, `any`, subscribe sans cleanup.

---

## Convention — Anti-tells IA (textes visibles)

CVForge vend l'anti-bullshit : son code ne doit pas trahir une génération IA. Dans toute chaîne destinée à l'affichage (templates Angular, constantes de texte, messages d'erreur backend, contenus statiques) :

- Trait d'union simple `-` (ou deux-points / parenthèses pour une incise). JAMAIS de tiret cadratin `—` ni demi-cadratin `–`.
- Apostrophe droite `'` et guillemets droits `"`. Pas les courbes. Exception : les guillemets français « » sont AUTORISÉS (vrais caractères FR).
- Trois points ASCII `...`, jamais l'ellipse unique `…`.
- Pas de flèches décoratives (`→ ← ⇒`) dans les textes UI (ok dans les diagrammes/docs).
- ⚠️ **Les lettres accentuées (é è à ç ù â ê î ô û ë ï ü œ æ) sont SACRÉES** : aucun remplacement automatique ne doit jamais les toucher. Le lint ne cible QUE la liste ci-dessus.
- Si un de ces caractères doit exister **fonctionnellement** dans le code (ex. table de translittération PDF qui les convertit), l'écrire en échappement `\uXXXX`, jamais en clair.
- Garde-fou : `npm run lint:tells` — couvre `frontend/src`, `prototypes/` ET `backend/app` (ts/html/json/md/css/js/py). Deux mailles supplémentaires depuis 2026-08-12 : un **hook pre-commit** (`.githooks/pre-commit`, activé par `core.hooksPath` — `node frontend/scripts/setup-hooks.mjs` après un clone) qui bloque le commit sur le même check, et une **règle ESLint** (`no-restricted-syntax`) qui l'attrape au lint dans les littéraux/templates TS.

---

## Definition of Done — V1

- 0 erreur TypeScript, 0 warning ESLint non justifié.
- Parcours complet fonctionnel : import CV → import offre → matching → adaptation → diff → export PDF, en **moins de 5 minutes**.
- Micro-tracking opérationnel (réponse ? entretien ? — 3 clics max).
- Fonctionne entièrement hors ligne, sauf l'appel LLM optionnel.
