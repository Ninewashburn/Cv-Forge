# CVForge — Roadmap Produit

> **MVP statement :** Prouver qu'une candidature basée sur des faits validés est meilleure qu'une candidature générée aveuglément.

**Corollaire :** la V1 embarque son propre instrument de mesure (micro-tracking). Sans mesure, le statement est un slogan.

**Dernière mise à jour :** 2026-06-26
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
  - Packaging desktop natif reporté en V1.5 — **exe portable PyInstaller** (le « sidecar Python » n'est plus un problème : Python EST l'exe). Mode installé + mode portable réconciliés par `resolve_data_dir()` câblée dès V1.
- [ ] **Schéma de données sync-ready dès le départ** : UUIDs, `created_at`/`updated_at`, soft deletes
  - La sync cloud est en V3, mais le schéma se décide **maintenant**
- [ ] **Stack confirmée** : Angular + FastAPI + SQLite
- [x] **Stratégie IA — TRANCHÉ** : 3 niveaux. Sans IA (toujours fonctionnel) → **Mode copilote** (prompt préparé + copier-coller vers le ChatGPT/Claude de l'utilisateur) → Clé API utilisateur. Ollama (IA 100% locale) reporté en V3.

---

## V0.5 — Édition « fichier unique » (livrée)

> Le chaînon manquant entre la feuille PDF et le logiciel : un seul fichier HTML **auto-sauvegardable** (pattern TiddlyWiki, 20 ans de preuve). Le fichier EST la base de données — copiable, partageable, archivable.

- [x] Core loop complet, zéro dépendance, double-clic
- [x] Auto-sauvegarde : File System Access API (Chrome/Edge — écrase le fichier après confirmation, puis 1 clic) + fallback téléchargement (Firefox/Safari)
- [x] Données embarquées en JSON dans le fichier (CV, offre, adaptation, micro-tracking)
- **Rôle stratégique** : véhicule de validation du MVP statement auprès des 20 testeurs AVANT les 3 mois de dev V1, et arme de distribution (un fichier qui se partage par mail/clé USB)
- **Limites assumées** (qui justifient la V1) : pas d'import PDF, pas de vrai export PDF/DOCX, pas de banque de preuves structurée, pas de multi-candidatures riches

---

## V0.5 — CVForge Lite : le fichier-application ✅

> **Le chaînon manquant entre le PDF et le logiciel.** Un seul fichier HTML = l'application + la base de données (pattern TiddlyWiki, éprouvé depuis 2004). « Enregistrer » réécrit le fichier lui-même avec les données dedans.

- [x] Core loop complet en 4 étapes : Sources (offre + CV côte à côte) → Analyse → Adaptation avec **matching live** → Diff & Export
- [x] Auto-sauvegarde dans le fichier : File System Access API (Chrome/Edge, écrasement en place avec confirmation native) + fallback téléchargement (Firefox/Safari)
- [x] Avertissement avant fermeture si modifications non enregistrées
- [ ] Distribution : un lien à partager, zéro installation, fonctionne sur n'importe quel poste (même verrouillé)
- [ ] Objectif : valider le MVP statement à grande échelle (bien au-delà des 20 testeurs)

**Garde-fou :** Lite ne grossit JAMAIS. Pas de pièces jointes (le base64 ferait exploser le fichier), preuves = texte + liens uniquement, pas d'historique de versions, une seule candidature active à la fois. Toute demande de plus = argument de vente pour la V1. **Lite est l'entonnoir, V1 est le produit.**

- [x] **Zone « révélation » LinkedIn — texte seul** *(entorse consciente et unique au gel, actée le 2026-06-26 ; livrée le 2026-06-28 : champ pointillé + tri 3 cases + double score, sans bouton auto)*
  - Inspiré d'un atelier RH (Michelin) : utiliser le profil LinkedIn comme **contexte de révélation**, version honnête. Spec complète en V1 ci-dessous.
  - **Pourquoi on déroge au gel** : ajout jugé **léger** (un champ optionnel + le tri 3 cases qui rejoue le matching déjà présent) et trop **aligné sur la philosophie anti-hallucination** pour être refusé.
  - **Reste texte-only dans Lite** : copier-coller du texte du profil, **aucun parsing PDF** (préserve le zéro-dépendance et le double-clic). Le parsing PDF est en V1.5.

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
    - *Prompt copilote **optionnel** — repérer les 5 compétences clés de l'offre* : « Lis cette offre d'emploi. Identifie les 5 compétences ou technologies les plus importantes, par ordre de priorité, en te basant UNIQUEMENT sur le texte de l'offre. Pour chacune, cite la phrase de l'offre qui la justifie. N'invente rien, ne note pas le candidat, ne suggère aucune compétence absente de l'offre. » → sortie = **liste brute** ; l'utilisateur décide ensuite quoi prouver. Le matching V1 reste **sans LLM** — ceci est un complément copilote **facultatif** (peut glisser en V1.5 si la V1 doit être allégée).
  - Clé API utilisateur (intégration directe, power users)
- [ ] **Diff Viewer** ⭐ — avant/après côte à côte, surlignage des modifications
  - **Killer feature, centre du pitch.** Preuve visuelle que rien n'est inventé.
  - Pas un diff git : lisible par tout public
- [ ] **Export PDF** propre (format simple, parsable)
- [ ] **Backup ZIP** — export/import complet des données (incarnation du "tes données t'appartiennent")
- [ ] **Micro-tracking** — 1 champ par candidature exportée : "réponse reçue ? entretien obtenu ?"
  - 3 clics max. Rend le MVP statement mesurable.
- [ ] **Zone « révélation » LinkedIn** ⭐ *(inspiré d'un atelier RH Michelin — le profil LinkedIn comme contexte, version honnête. Aussi en Lite, texte seul.)*
  - **Principe — deux statuts de données, jamais confondus :**
    - *Source de vérité* = le CV. C'est ce qui est adapté et exporté.
    - *Sources de révélation* (LinkedIn ; plus tard GitHub/portfolio) = éclairent les trous, **n'entrent JAMAIS dans la source de vérité sans décision explicite**.
  - **UI** : champ optionnel **visuellement distinct** du CV (bordure pointillée, fond grisé) pour signaler son statut différent. Titre « Profil LinkedIn — optionnel, pour repérer ce qui manque ». Tooltip « Télécharge ton profil LinkedIn en PDF, puis copie-colle le texte ici. »
  - **Comportement** — à l'analyse, tri à **3 cases** de chaque mot-clé de l'offre :
    1. Sur ton CV (**vert**) — déjà couvert.
    2. Sur LinkedIn mais absent du CV (**orange, ACTIONNABLE**) — « Tu mentionnes X sur LinkedIn. L'offre le demande. L'ajouter à ton CV ? »
    3. Nulle part (**gris, prudence**) — « Ni CV ni LinkedIn : ne pas inventer. »
  - **Règle anti-fusion (NON NÉGOCIABLE)** : « Ajouter X » **n'écrit PAS** dans le CV — ça pré-remplit une **suggestion** que l'utilisateur intègre lui-même → elle apparaît dans le **Diff** → rituel « vrai et prouvable ? ». *LinkedIn révèle, l'utilisateur décide, le Diff trace.* **INTERDIT** : verser automatiquement les compétences LinkedIn dans la base d'adaptation — gonfler la source en amont vide le Diff de son sens (= geste WorkMachine).
  - **Double score (honnêteté d'un cran)** : « ton CV couvre 55 % » **et** « CV + ce que tu peux légitimement ajouter depuis LinkedIn : 71 % ». Le second est un **potentiel/objectif, jamais un score envoyé**.
  - **Périmètre V1** : copier-coller **texte uniquement** (pas de parsing PDF — voir V1.5). Même contrat en Lite.

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
- [ ] **CV Linter — la règle des 6P** *(Préparation, Préparation, Préparation : Postulat Par Preuve)* — détection automatique des anti-patterns, sans IA :
  - Barres/pourcentages de compétences (« Angular 80% » = 80% de quoi ?)
  - Clichés de motivation non prouvés (« passionné par… ») → suggérer une preuve d'intérêt à la place
  - Adjectifs creux en rafale (dynamique, motivé, rigoureux…) sans fait chiffré à proximité
  - Icônes/caractères décoratifs qui cassent le parsing ATS
- [ ] **Versioning CV** — revenir à une version antérieure
- [ ] **Parsing PDF — profils & offres** *(couche optionnelle de la « Zone révélation » — spec en V1 ; LinkedIn d'abord, plus tard Indeed/APEC)* — extraction texte **côté FastAPI** (Lite reste en copier-coller manuel, aucun parsing). Le texte extrait = **source de révélation** (gap analysis), **jamais d'auto-fusion** dans le CV ; réutilise le contrat déjà défini : preuve candidate → validation → Avant/Après. **Robustesse** : le format PDF LinkedIn change souvent (multilingue, sections déplacées) → prévoir un parsing **tolérant** + **fallback « colle le texte à la main »** si l'extraction échoue. **Statut : non garanti** — le copier-coller texte (V1 + Lite) peut suffire. Pas d'appel réseau : l'utilisateur fournit le fichier.
- [ ] **Anonymisation / caviardage avant copilote** *(d'après un conseil RH — Philippe : « anonymise ton CV avant de l'envoyer à l'IA »)* — bouton **« Anonymiser »** qui masque, **avant** la génération du prompt copilote : nom, prénom, email, téléphone, adresse, liens personnels → remplacés par des marqueurs neutres (`[NOM]`, `[EMAIL]`…), réversibles en local. **Le CV réel n'est jamais modifié** ; seul le texte *envoyé* à l'IA est caviardé. Sert directement la confidentialité (cœur local-first), pas un gadget : il renforce preuve + contrôle. **Statut : V1.5+**.
- [ ] **Export DOCX basique** *(remonté de V3 — beaucoup de RH exigent encore Word)*
- [ ] **Packaging desktop — exe portable façon ADWCleaner** : PyInstaller `--onefile` (Python + FastAPI + build Angular dans un seul exécutable). Double-clic → serveur local → navigateur. **Données : résolues par `resolve_data_dir()` (câblée dès V1)** — défaut `~/.cvforge/` (mode installé, données préservées si on remplace l'exe) ; mode portable activé par un marqueur `cvforge.portable` à côté de l'exe → données dans `./data/` qui voyagent sur la clé USB. Le même binaire fait les deux. Option fenêtre native : pywebview (WebView2). Signature de code à prévoir contre SmartScreen (Azure Trusted Signing ~10 $/mois). Pas d'UPX (faux positifs antivirus). Tauri abandonné — plus nécessaire.

### Stratégie de diffusion (le pendant du packaging)

> 🔒 **Contenu GTM extrait hors du dépôt** (pour rester publiable) → voir `private/STRATEGIE.md` (non versionné).
> Résumé neutre, sans risque : exe `--onefile` distribué via **GitHub Releases**, données créées au runtime par `resolve_data_dir()` (rien dans le téléchargement), entonnoir via la démo Lite en ligne.

---

## V2 — Suivi & Préparation (~+3 mois)

> Du document à la démarche.

- [ ] **Suivi candidatures** — **5 statuts max** : À envoyer / Envoyée / Entretien / Refusée / Acceptée + **contact par candidature** (nom, email, coordonnées du recruteur — premier pas vers l'angle réseau)
- [ ] **Dashboard** — "que dois-je faire aujourd'hui ?" : rappels, relances, entretiens à venir
- [ ] **Calendrier de relances** — "relancer Entreprise X dans 7 jours si pas de réponse"
- [ ] **Préparation entretien — la grille des 5P** *(d'après Philippe, RH Michelin — grille de PRÉPARATION, jamais dans le prompt d'adaptation du CV qui reste factuel)* — une section par P, remplie **à partir de faits réels** (banque de preuves), jamais d'éléments inventés (l'outil **structure**, ne fabrique pas) :
  1. **Pourquoi cette entreprise ?** (recherche, actualité, valeurs)
  2. **Poste visé** (ce que le rôle demande vraiment)
  3. **Parcours professionnel** (le fil narratif, pas la liste)
  4. **Personnalité** (forces, façon de travailler — prouvables par des exemples)
  5. **Pitch** (présentation courte, **chronométrée 60-90 s**)
  - + questions probables et notes post-entretien.
  - ⚠️ **Ne pas confondre avec la règle des 6P du CV Linter (V1.5)** : les **5P** = préparation entretien ; les **6P** = anti-patterns du CV. Deux grilles distinctes.
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
| 6 | Emplacement données : installé (`~/.cvforge/`) vs portable (clé USB) se contredisent | `resolve_data_dir()` unique, câblée dès V1, jamais de chemin en dur. Le marqueur `cvforge.portable` choisit le mode. |

---

## Paysage concurrentiel & positionnement

> 🔒 **Analyse concurrentielle et positionnement défensif extraits hors du dépôt** (sensibles si le repo devient public) → voir `private/STRATEGIE.md` (non versionné).

---

## Vision en une phrase

**CVForge : candidater comme on code — avec méthode, traçabilité, sans bullshit.**

*Chercher un emploi n'est pas postuler au hasard. C'est avancer avec méthode.*
