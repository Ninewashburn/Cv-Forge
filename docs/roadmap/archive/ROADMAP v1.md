# CVForge — Roadmap Produit

> **MVP statement :** Prouver qu'une candidature basée sur des faits validés est meilleure qu'une candidature générée aveuglément.

**Corollaire :** la V1 embarque son propre instrument de mesure (micro-tracking). Sans mesure, le statement est un slogan.

**Dernière mise à jour :** 2026-06-10
**Statut :** V0 tranché — prêt pour Claude Code (voir CLAUDE.md)
**Maquettes :** les schémas d'interface = vision cible (North Star, V3+). Le périmètre de build reste la section V1, exclusivement.

---

## Principes non négociables

1. **Anti-hallucination** — l'outil reformule, réorganise, priorise. Il n'invente jamais une compétence, une expérience, une techno.
2. **Local-first / privacy** — données locales, fonctionne sans compte, cloud optionnel uniquement.
3. **Preuve par les faits** — chaque affirmation du CV reliée à une preuve dans la banque.
4. **Tout public** — zéro jargon tech dans l'UI. Le produit est universel, la *distribution* est ciblée (devs francophones, reconversions RNCP).
5. **IA optionnelle** — toute fonctionnalité core fonctionne sans LLM. L'IA accélère, elle ne porte pas.

---

## V0 — Décisions d'architecture (AVANT la première ligne de code)

> Objectif : éviter les dettes structurelles irréversibles.

- [x] **Packaging — TRANCHÉ** : V1 = web app locale. FastAPI sert le build Angular, un seul process, lancement par script double-cliquable (`start.bat` / `start.sh`) qui ouvre le navigateur sur `localhost:8000`.
  - Cross-platform gratuit (Windows/Mac/Linux), zéro temps de packaging avant validation du produit
  - Packaging desktop natif reporté en V1.5 — Tauri pressenti (v2 couvre aussi Android/iOS), sidecar Python à résoudre à ce moment-là
- [ ] **Schéma de données sync-ready dès le départ** : UUIDs, `created_at`/`updated_at`, soft deletes
  - La sync cloud est en V3, mais le schéma se décide **maintenant**
- [ ] **Stack confirmée** : Angular + FastAPI + SQLite
- [x] **Stratégie IA — TRANCHÉ** : 3 niveaux. Sans IA (toujours fonctionnel) → **Mode copilote** (prompt préparé + copier-coller vers le ChatGPT/Claude de l'utilisateur) → Clé API utilisateur. Ollama (IA 100% locale) reporté en V3.

---

## V1 — Core Loop (~3 mois)

> **Une seule chose bien faite :** coller une offre + un CV → adaptation tracée → export PDF.

### Features

- [ ] **Import CV existant** (PDF/texte) → pré-remplissage du profil maître
  - Anti-mur d'onboarding : valeur visible en < 5 min
- [ ] **Import offre** (copier-coller texte ou URL)
- [ ] **Profil maître simple** — source de vérité, champs essentiels uniquement
- [ ] **Banque de preuves simple** — texte, lien, document (GitHub = *un type* de preuve parmi d'autres)
- [ ] **Matching mots-clés sans LLM** — fréquence, couverture des exigences de l'offre
- [ ] **Adaptation contrôlée** — 3 niveaux :
  - Manuelle (sans IA, toujours disponible)
  - **Mode copilote** : prompt verrouillé généré par CVForge (anti-hallucination inclus) → copier-coller vers le ChatGPT/Claude de l'utilisateur (nouvel onglet) → retour validé par le Diff Viewer. Zéro clé API, zéro coût.
  - Clé API utilisateur (intégration directe, power users)
- [ ] **Diff Viewer** ⭐ — avant/après côte à côte, surlignage des modifications
  - **Killer feature, centre du pitch.** Preuve visuelle que rien n'est inventé.
  - Pas un diff git : lisible par tout public
- [ ] **Export PDF** propre (format simple, parsable)
- [ ] **Backup ZIP** — export/import complet des données (incarnation du "tes données t'appartiennent")
- [ ] **Micro-tracking** — 1 champ par candidature exportée : "réponse reçue ? entretien obtenu ?"
  - 3 clics max. Rend le MVP statement mesurable.

### Critères de sortie V1

- [ ] 20 testeurs réels ont complété le core loop de bout en bout
- [ ] Feedback qualitatif + taux de réponse collectés via micro-tracking
- [ ] Onboarding : première valeur en moins de 5 minutes

### Hors scope V1 (explicite, non négociable)

Dashboard · suivi complet · préparation entretien · app mobile · extension navigateur · multilingue · Ollama · sync cloud · interface 3 colonnes

---

## V1.5 — Crédibilité (~+2 mois)

> Rendre les exports fiables face aux filtres réels.

- [ ] **ATS Checker (scope honnête)** :
  - Parsabilité du PDF : texte extractible, structure simple, pas de colonnes piégeuses
  - Couverture des mots-clés critiques de l'offre
  - ❌ Pas de simulation Taleo/Workday — ne jamais promettre ce qu'on ne fait pas
- [ ] **Versioning CV** — revenir à une version antérieure
- [ ] **Export DOCX basique** *(remonté de V3 — beaucoup de RH exigent encore Word)*
- [ ] **Packaging desktop** — installateur double-clic Win/Mac/Linux (Tauri pressenti, sidecar Python via PyInstaller)

---

## V2 — Suivi & Préparation (~+3 mois)

> Du document à la démarche.

- [ ] **Suivi candidatures** — **5 statuts max** : À envoyer / Envoyée / Entretien / Refusée / Acceptée
- [ ] **Dashboard** — "que dois-je faire aujourd'hui ?" : rappels, relances, entretiens à venir
- [ ] **Calendrier de relances** — "relancer Entreprise X dans 7 jours si pas de réponse"
- [ ] **Préparation entretien** — pitch, questions probables, notes post-entretien
- [ ] **Fiche mémo entretien** — consultable/imprimable juste avant l'entretien
- [ ] **Analyse d'offre : signaux faibles** — détection points positifs / red flags d'une offre (issu des maquettes — bonne idée à conserver)

> *"Historique" supprimé de la liste initiale — redondant avec Versioning (V1.5) et Suivi (V2).*

---

## V2.5 — Capture : "le geste Forge" (~+2 mois)

> Un seul concept — sauvegarder une offre en 1 geste — deux portes d'entrée : extension navigateur (desktop, V2.5) et partage mobile (V3).

- [ ] **Extension navigateur "Envoyer à la Forge"**
  - Capture d'offre en 1 clic depuis LinkedIn / Indeed / HelloWork / WTTJ
  - Manifest V3, Chrome d'abord, Firefox ensuite

---

## V3 — Expansion technique

- [ ] **App mobile compagnon** (Angular + Capacitor — réutilise les composants du frontend) — journal de candidatures en lecture, pitch, rappels + **capture d'offre via Android Share Target** ("Partager vers CVForge" depuis l'app LinkedIn/Indeed). Pas d'édition de CV.
  - ⚠️ **Dépend de la sync cloud** : une app mobile ne peut pas parler au SQLite du PC sans elle. Ordre imposé : sync d'abord, mobile ensuite.
- [ ] **Ollama local (IA 100% locale)** — installation guidée depuis l'app : clic → écran de consentement honnête (~5 Go de téléchargement, 8+ Go RAM requis, qualité inférieure aux modèles cloud) → vérification RAM/disque → install + pull du modèle. Fallback mode copilote / clé API conservé.
- [ ] **Sync cloud optionnelle** — le schéma sync-ready de V0 paie ici
- [ ] **Export DOCX avancé** — templates, mise en page fine

---

## V4+ — Vision long terme

- [ ] Multilingue / international
- [ ] Projet professionnel complet (métiers visés, contraintes, motivations)
- [ ] Partage avancé — lien temporaire, suivi de consultation
- [ ] Intégrations LinkedIn / GitHub — import automatique de preuves
- [ ] Simulation entretien difficile — stress test : "Tu mets Spring Boot ? Réponds à ces 3 questions."

---

## Supprimé / refusé

| Idée | Raison |
|---|---|
| 11 statuts de candidature | Sur-complexité. 5 suffisent. |
| Agrégation multi-sources d'offres | Ne pas recréer Indeed. Le copier-coller suffit. |
| Module savoir-être / forces naturelles | Subjectif, hors périmètre d'un outil de preuve. |
| Banque de formulations génériques | Contre-philosophie : c'est exactement le bullshit qu'on combat. |
| Interface 3 colonnes en V1 | Power user only. Mode guidé linéaire d'abord. |

---

## Risques actifs

| # | Risque | Parade |
|---|---|---|
| 1 | Mur d'onboarding (profil maître trop long) | Import CV obligatoire en V1, valeur < 5 min |
| 2 | Substitution Notion + LLM | Diff Viewer + banque de preuves = ce qu'un LLM générique ne fait pas |
| 3 | Packaging non tranché | Décision V0, bloque tout le reste |
| 4 | Scope creep | Toute nouvelle idée va en V4+, jamais en V1 |
| 5 | Sync cloud improvisée plus tard | Schéma sync-ready dès V0 |

---

## Vision en une phrase

**CVForge : candidater comme on code — avec méthode, traçabilité, sans bullshit.**

*Chercher un emploi n'est pas postuler au hasard. C'est avancer avec méthode.*
