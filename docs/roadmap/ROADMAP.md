# CVForge — Roadmap Produit

> **MVP statement :** Prouver qu'une candidature basée sur des faits validés est meilleure qu'une candidature générée aveuglément.

**Corollaire :** la V1 embarque son propre instrument de mesure (micro-tracking). Sans mesure, le statement est un slogan.

**Dernière mise à jour :** 2026-07-12
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
- [x] **Schéma de données sync-ready dès le départ** : UUIDs, `created_at`/`updated_at`, soft deletes *(livré Phase 0, 2026-07)*
  - La sync cloud est en V3, mais le schéma se décide **maintenant**
- [x] **Stack confirmée** : Angular + FastAPI + SQLite *(en production locale depuis les Phases 1-3)*
- [x] **Stratégie IA — TRANCHÉ** : 3 niveaux. Sans IA (toujours fonctionnel) → **Mode copilote** (prompt préparé + copier-coller vers le ChatGPT/Claude de l'utilisateur) → Clé API utilisateur. Ollama (IA 100% locale) reporté en V3.
- [x] **Licence — TRANCHÉ : MIT sec** *(2026-07-02, sur précédent de projets voisins local-first)* — CVForge n'embarque aucun modèle ni composant tiers → MIT simple, sans NOTICE. Tout converge vers l'open source : le moat est la **philosophie** (pas le code), la preuve local-first exige un code auditable (« vérifie toi-même »), et la confiance au téléchargement en dépend.

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
- [x] **Mini-FAQ confiance in-app** *(2026-07-02 — contenu statique, pas une feature : le gel tient)* — dépliant discret à l'étape Sources, 4 questions : où vont mes données / faut-il installer / ça écrit à ma place ? / comment je garde mon travail. Rassure au moment exact où l'utilisateur hésite à coller son CV, et laisse entrevoir le produit complet (« une version application, à emporter partout, viendra plus tard »). Nuance d'honnêteté copilote incluse : c'est l'utilisateur qui colle son texte dans son IA — CVForge, lui, n'envoie jamais rien. À décliner en V1 (même contenu) et en README (version dev, vérifiable).

---

## V1 — Core Loop (~3 mois)

> **Une seule chose bien faite :** coller une offre + un CV → adaptation tracée → export PDF.

### Features

- [x] **Import CV existant** (PDF/texte) → pré-remplissage du profil maître *(livré 2026-07-11 : import fichier → zone CV du wizard **et** bloc « CV complet » de la vue Profil ; le matching et le copilote s'en servent automatiquement)*
  - Anti-mur d'onboarding : valeur visible en < 5 min
- [x] **Import offre** — copier-coller texte (l'URL n'est qu'une référence saisie, **jamais fetchée** — règle « aucun réseau sortant »)
- [x] **Bouton « Importer un fichier » sur chaque zone de texte** (CV, offre, profil LinkedIn) *(ajout 2026-07-02 ; livré 2026-07-11 — `POST /api/extract`, pypdf)*
  - Extraction de texte **locale** (pypdf : PDF + .txt) côté FastAPI — le fichier ne quitte jamais la machine.
  - Le texte extrait atterrit dans le champ, **visible et éditable avant toute analyse** — même contrat que le copier-coller, qui reste toujours disponible (fallback universel).
  - Un seul endpoint générique réutilisé par les trois champs. **Hors Lite** (gel : zéro backend).
- [x] **Profil maître simple** — source de vérité, champs essentiels uniquement *(livré 2026-07-11 : vue « Profil & Preuves »)*
- [x] **Banque de preuves simple** — texte, lien, document (GitHub = *un type* de preuve parmi d'autres) *(livré 2026-07-11 : faits ↔ preuves liés, pièce jointe locale sous `<data>/proofs/`, embarquée dans le backup ZIP)*
- [x] **Matching mots-clés sans LLM** — fréquence, couverture des exigences de l'offre
- [x] **Adaptation contrôlée** — 3 niveaux *(complet 2026-07-11 : manuelle + copilote 4 intentions + **clé API utilisateur** — Anthropic/Claude en V1, consentement explicite avec affichage de ce qui est envoyé, clé stockée côté backend et **exclue du backup ZIP** ; autres fournisseurs → V1.5)* :
  - Manuelle (sans IA, toujours disponible)
  - **Mode copilote** : prompt verrouillé généré par CVForge (anti-hallucination inclus) → copier-coller vers le ChatGPT/Claude de l'utilisateur (nouvel onglet) → retour validé par le Diff Viewer. Zéro clé API, zéro coût.
    - *Prompt copilote **optionnel** — repérer les 5 compétences clés de l'offre* : « Lis cette offre d'emploi. Identifie les 5 compétences ou technologies les plus importantes, par ordre de priorité, en te basant UNIQUEMENT sur le texte de l'offre. Pour chacune, cite la phrase de l'offre qui la justifie. N'invente rien, ne note pas le candidat, ne suggère aucune compétence absente de l'offre. » → sortie = **liste brute** ; l'utilisateur décide ensuite quoi prouver. Le matching V1 reste **sans LLM** — ceci est un complément copilote **facultatif** (peut glisser en V1.5 si la V1 doit être allégée).
    - **Bibliothèque de prompts verrouillés** *(ajout 2026-07-02 — spec canonique : `docs/specs/copilot_prompts.md`)* — 4 intentions, sélecteur **Adapter / Auditer / Muscler / Accrocher** au-dessus du bouton « Préparer le prompt » (Adapter = défaut) :
      1. **ADAPTER** — le prompt principal existant (verrou + Avant/Après obligatoire).
      2. **AUDITER** — critique de recruteur exigeant, **ne réécrit rien**, chaque faiblesse citée + question pour la renforcer avec un fait réel.
      3. **MUSCLER** — verbes d'action à partir des faits existants ; chiffre absent = jamais inventé, listé « **À chiffrer par le candidat** ».
      4. **ACCROCHER** — accroche 3 lignes max, que du vérifiable, adjectifs autoproclamés interdits.
      - Pattern commun : **ce qui manque n'est jamais ajouté, il est listé « À compléter par le candidat »**. Rejetés : « ATS Boost » (= stuffing), « Format Fix » (→ CV Linter V1.5), « Cover Letter » (→ V2, message de motivation).
  - Clé API utilisateur (intégration directe, power users)
- [x] **Diff Viewer** ⭐ — avant/après côte à côte, surlignage des modifications
  - **Killer feature, centre du pitch.** Preuve visuelle que rien n'est inventé.
  - Pas un diff git : lisible par tout public
- [x] **Export PDF** propre (format simple, parsable)
- [x] **Backup ZIP** — export/import complet des données (incarnation du "tes données t'appartiennent")
- [x] **Micro-tracking** — 1 champ par candidature exportée : "réponse reçue ? entretien obtenu ?"
  - 3 clics max. Rend le MVP statement mesurable.
- [x] **Zone « révélation » LinkedIn** ⭐ *(inspiré d'un atelier RH Michelin — le profil LinkedIn comme contexte, version honnête. Aussi en Lite, texte seul.)*
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
- [x] **Layout « établi » de l'Atelier** *(ajout 2026-07-08, livré 2026-07-10 ; retour visuel : « des petits encadrés pour travailler, c'est frustrant »)* — l'Atelier est un **espace de travail**, pas une page de lecture ; l'Accueil, lui, reste étroit (confort de lecture ~1060px). Repère : **la V1 ne doit jamais être plus étriquée que Lite (1280px)**.
  1. **Largeur fluide réservée à l'Atelier** : `min(~1440px, 94vw)`.
  2. **Hauteurs pilotées par l'écran, jamais en pixels fixes** : Sources ≈ 55vh ; Adaptation et Avant/Après remplissent la hauteur restante du viewport (`100dvh − chrome`) — sensation « éditeur ».
  3. **Chrome vertical dégraissé** dans l'Atelier : masthead compact, intro raccourcie (~120px récupérés).
  4. Bonus : `field-sizing: content` (auto-grow des textareas, progressive enhancement — Chrome/Edge OK, fallback min-height ailleurs).
  - Plus tard (polish optionnel, ne pas coder avant le core loop) : bouton « agrandir » par volet / mode focus. L'instinct « l'espace de travail domine » = maquettes North Star, on y répond par le layout, pas en avançant la V3.
- [x] **Mini-FAQ confiance in-app (V1)** *(livré 2026-07-10)* — décliner dans l'Atelier (étape Sources) le dépliant 4 questions déjà livré dans Lite. ⚠️ Adapter la réponse « Comment je garde mon travail ? » à la V1 : le fichier n'est plus la sauvegarde — les données vivent dans `~/.cvforge/` (SQLite, enregistrement automatique), et le **backup ZIP** est l'incarnation « tes données t'appartiennent ». Les 3 autres réponses restent valables telles quelles.

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
  - **Chiffre non rattaché à une preuve de la banque** (« délais réduits de 30 % » sans proof liée) → alerte « peux-tu prouver ce chiffre en entretien ? » *(ajout 2026-07-11)*. Règle : **chiffre ce que tu as mesuré, décris qualitativement ce que tu n'as pas mesuré — n'invente jamais un chiffre pour faire sérieux.** Le conseil générique « quantifiez vos résultats », répandu partout, pousse à inventer des chiffres plausibles : c'est exactement ce que CVForge refuse. À intégrer aussi au prompt d'audit copilote.
  - Icônes/caractères décoratifs qui cassent le parsing ATS
- [ ] **Confirmation Avant/Après reliée à la banque de preuves** *(ajout 2026-07-28, retour test réel — concrétise la promesse déjà affichée « Bientôt, chaque confirmation se reliera à ta banque de preuves »)* — à côté de chaque bouton « Confirmer — vrai et prouvable », un champ **optionnel** « Comment ? / écris ici ta preuve » (ex. « Chez X, j'ai mis en place le pipeline CI/CD : build, lint, test »). Au clic « Confirmé », si le champ est rempli → **créer une preuve** (type note) dans Profil & Preuves, reliée au fait correspondant. Boucle vertueuse : l'ajout au CV devient une preuve réutilisable, et l'utilisateur muscle sa banque sans quitter son parcours. Ne jamais forcer : vide = simple confirmation, comme aujourd'hui.
- [ ] **Matching plus tolérant — mots voisins / lemmatisation légère** *(ajout 2026-07-28, retour test réel)* — aujourd'hui « déployer » (mot-clé de l'offre) et « déploiement » (écrit dans le CV) ne se rapprochent pas : le stemming minimal ne réunit pas verbe et nom d'une même racine, ni les variantes orthographiques (déploie-/déploy-). Piste : lemmatisation légère FR ou table de familles de mots, **sans** sur-généraliser (le sur-matching donnerait un faux score de couverture — pire que l'inverse). À valider sur des offres réelles ; le mode IA optionnel pourrait aussi couvrir ce besoin plus tard. **Statut : à confirmer.**
- [ ] **Niveau clé API — fournisseurs supplémentaires** (OpenAI…) *(ajout 2026-07-11 ; V1 = Anthropic uniquement, un seul SDK embarqué)* — même contrat que le niveau livré : prompt système anti-hallucination imposé, consentement explicite, proposition validée dans l'Avant/Après.
- [ ] **Versioning CV** — revenir à une version antérieure
- [ ] **Parsing structuré des PDF LinkedIn** *(l'extraction **brute** est couverte dès V1 par le bouton « Importer un fichier » — voir V1)* — reste en V1.5 uniquement la **structuration robuste** si l'extraction brute ne suffit pas : reconnaissance des sections LinkedIn (Expérience, Compétences…), formats multilingues, sections déplacées → parsing **tolérant** + fallback « colle le texte à la main ». Même contrat : source de révélation, **jamais d'auto-fusion**, validation par l'Avant/Après. **Statut : non garanti** — à confirmer selon l'usage réel. Pas d'appel réseau : l'utilisateur fournit le fichier.
- [ ] **Anonymisation / caviardage avant copilote** *(d'après un conseil RH — Philippe : « anonymise ton CV avant de l'envoyer à l'IA »)* — bouton **« Anonymiser »** qui masque, **avant** la génération du prompt copilote : nom, prénom, email, téléphone, adresse, liens personnels → remplacés par des marqueurs neutres (`[NOM]`, `[EMAIL]`…), réversibles en local. **Le CV réel n'est jamais modifié** ; seul le texte *envoyé* à l'IA est caviardé. Sert directement la confidentialité (cœur local-first), pas un gadget : il renforce preuve + contrôle. **Statut : V1.5+**.
- [ ] **Audit de sécurité avant déploiement — VICE** *(ajout 2026-07-05 ; github.com/Webba-Creative-Technologies/vice, MIT, npm `vice-security`)*
  - **Mode local / white-box uniquement** : `vice audit .` — lit le code source, **ne lance aucune attaque**, sans risque. Modules pertinents : *Code Vulnerabilities* (XSS/eval/SQLi) + *Dependencies* (npm audit du frontend Angular).
  - **NE PAS utiliser le mode remote** (`vice scan`) : il lance de vraies attaques (brute force, injection SQL, scan de ports) et vise des apps serveur. CVForge est local-first **sans serveur** → non applicable, et juridiquement à éviter sur toute URL non strictement auto-hébergée (GitHub Pages = infra GitHub incluse).
  - **Point de vigilance prioritaire — l'Avant/Après (Diff Viewer)** : il met en forme du texte collé par l'utilisateur. C'est **LA vraie surface d'attaque** de CVForge (pas l'infra, qui n'existe pas). Vérifier qu'aucune XSS ne passe. *Côté Angular V1 : l'interpolation `{{ }}` échappe par défaut ; ne JAMAIS passer le texte utilisateur brut à `[innerHTML]` sans DomSanitizer.* Côté Lite : la fonction `esc()` joue ce rôle.
  - **Bonus open source** : badge de sécurité VICE (score A–F) + GitHub Action sur les PR → signal de confiance vérifiable sur le README, cohérent avec la promesse « vos données sont en sécurité ». À activer quand le repo passe public.
- [ ] **Convention anti-tells IA — outillage** *(ajout 2026-07-12 ; règle complète dans CLAUDE.md)* — aucun caractère « signature IA » (tirets cadratins, ellipse unique, quotes courbes, flèches) dans les textes visibles ; les accents français ne sont jamais touchés par le lint. *(fait 2026-07-12 : purge des sources frontend + backend, script `npm run lint:tells` ; **reste : hook pre-commit qui bloque le commit + règle ESLint dédiée** pour l'attraper au lint)*
- [ ] **Export DOCX basique** *(remonté de V3 — beaucoup de RH exigent encore Word)*
- [ ] **Packaging desktop — exe portable façon ADWCleaner** : PyInstaller `--onefile` (Python + FastAPI + build Angular dans un seul exécutable). Double-clic → serveur local → navigateur. **Données : résolues par `resolve_data_dir()` (câblée dès V1)** — défaut `~/.cvforge/` (mode installé, données préservées si on remplace l'exe) ; mode portable activé par un marqueur `cvforge.portable` à côté de l'exe → données dans `./data/` qui voyagent sur la clé USB. Le même binaire fait les deux. Option fenêtre native : pywebview (WebView2). Signature de code à prévoir contre SmartScreen (Azure Trusted Signing ~10 $/mois). Pas d'UPX (faux positifs antivirus). Tauri abandonné — plus nécessaire.

### Stratégie de diffusion (le pendant du packaging)

> 🔒 **Contenu GTM extrait hors du dépôt** (pour rester publiable) → voir `private/STRATEGIE.md` (non versionné).
> Résumé neutre, sans risque : exe `--onefile` distribué via **GitHub Releases**, données créées au runtime par `resolve_data_dir()` (rien dans le téléchargement), entonnoir via la démo Lite en ligne.

**Patterns de présentation actés (réf. projets voisins local-first, 2026-07-02) :**
- **Bloc confiance en tête de README** — format question frontale → réponse en un mot → détail (« Mes données partent-elles quelque part ? » → **Jamais.** Pas de cloud, pas de compte, pas de télémétrie…). Ce bloc vaut mieux que dix paragraphes de philosophie. Version README = **factuelle et vérifiable** pour le public dev : « aucun appel réseau sortant sauf l'appel LLM que VOUS déclenchez — vérifiable dans le code ». Le dev ne veut pas être rassuré, il veut une preuve.
- **Honnêteté de statut** — ne JAMAIS annoncer ce qui n'est pas testé (README, releases, posts). La démo est réellement en ligne AVANT l'annonce.
- **FAQ confiance = même vérité, quatre habillages** : in-app (rassurer au moment du doute) / README (prouver au dev) / post (raconter pour sensibiliser) / site (présenter au curieux). Jamais une version passe-partout. Nuance obligatoire partout : CVForge n'envoie rien ; en mode copilote c'est **l'utilisateur** qui colle son texte dans son IA, en le sachant.
- Patterns communautaires détaillés (post de lancement, angle accessibilité) → `private/STRATEGIE.md`.

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
- [ ] **CV semi-structuré — sections repliables et éditables indépendamment** *(ajout 2026-07-27, d'après retour test réel)* — remplacer le textarea unique de l'étape Adaptation par des sections (En-tête / Expériences / Compétences / Formation...) éditables séparément.
  - **Pourquoi V2 et pas correctif d'ergonomie** : c'est un **changement de modèle de données** (le CV n'est plus une chaîne brute), à impact large — API, stockage, ET le Diff (l'Avant/Après compare aujourd'hui du texte brut via `lcsDiff` ; comparer section par section serait plus juste mais complexifie nettement l'algorithme). À réfléchir posément, pas en catimini.
  - **Déjà livré en V1 comme substitut affichage-seul** *(2026-07-27)* : dans l'étape Adaptation, surlignage live des mots-clés couverts (vert) + repères des lignes de section (teinte), en overlay derrière le textarea — le CV reste une chaîne brute, aucun changement de modèle. Ça rapproche visuellement l'étape 3 de l'Avant/Après sans en payer le coût. Le semi-structuré reste la vraie évolution V2 si le besoin se confirme.

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

- [ ] **Multilingue / international** — le produit est universel (tout public, tout pays) ; la V1 reste français-first (la *distribution* est ciblée, pas le produit). À câbler comme des **packs de langue**, jamais des refontes :
  - **UI** : sélecteur de langue (i18n Angular), textes externalisés une fois le wizard V1 stabilisé.
  - **Moteur de mots-clés** : stop-words + stemming sont **par langue** — aujourd'hui FR, isolés dans un module pur unique (`keyword_engine.py`) → ajouter l'anglais = un pack de plus, pas un refactor.
  - **Prompt copilote** : un template par langue.
  - **Export PDF** : libellés de sections traduits.
  - **Données** : déjà neutres (UUID, timestamps, schéma sync-ready) — rien à migrer.
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
