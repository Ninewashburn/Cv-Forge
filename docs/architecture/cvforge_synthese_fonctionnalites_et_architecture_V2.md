# CVForge — Synthèse V2 des fonctionnalités, architecture cockpit et décisions produit

> Cette version consolide le fichier initial et ajoute les décisions ergonomiques récentes : candidature active comme centre fonctionnel, navigation en trois niveaux, tableau de bord, atelier, suivi global/contextuel, règles d’usage des tiroirs et scoring d’opportunité.

---

## Objectif du document

Ce document regroupe les idées, arbitrages et fonctionnalités évoqués depuis les modules de rappels / notifications jusqu’aux dernières réflexions sur l’assistance IA, le suivi intelligent, l’interface, l’usage desktop/mobile, l’inspiration Blip et la préparation d’entretien.

Ce n’est pas un cahier des charges figé. C’est une base de réflexion à placer dans le projet pour guider Codex ou l’IDE.

La V1 locale servira à trier ce qui doit être :

```txt
À garder
À simplifier
À améliorer
À retirer
À repousser
```

---

## 1. Vision produit consolidée

CVForge doit être un assistant de candidature local-first.

Il aide l’utilisateur à :

- structurer son parcours ;
- relier ses compétences à des preuves ;
- sauvegarder des offres ;
- adapter son CV à une offre ;
- écrire un message court ;
- préparer un pitch ;
- préparer un entretien ;
- suivre ses candidatures ;
- créer des rappels ;
- centraliser ses documents ;
- garder le contrôle sur ses données.

Promesse centrale :

> Adapter ses candidatures à chaque offre, sans inventer son parcours et sans perdre le contrôle de ses données.

Règle fondatrice :

```txt
Pas de phrase sans fait.
Pas de fait sans validation.
Pas de donnée envoyée sans consentement.
```

CVForge ne doit pas être présenté comme “une IA qui refait votre CV”. Il doit être présenté comme un cockpit personnel de candidature.

---

## 2. Confiance, données personnelles et import CV

### Principe

CVForge ne doit pas collecter les CV pour exploiter des données.

Cela ne veut pas dire que l’application ne stocke rien. Cela signifie que les données sont stockées localement par défaut, sous le contrôle de l’utilisateur.

### Formulation produit recommandée

```txt
Vos données restent sur votre appareil.
Aucun compte n’est nécessaire.
Votre CV n’est pas utilisé pour entraîner une IA.
Vos offres, preuves et documents ne sont pas envoyés à un serveur CVForge.
Vous choisissez explicitement ce que vous partagez.
```

### Import CV

L’import CV doit être présenté comme une aide au préremplissage, pas comme une collecte.

Formulation recommandée :

```txt
Préremplir mon parcours depuis un CV local.
```

Explication :

```txt
Votre CV sert uniquement à préremplir votre parcours sur cet appareil.
Les informations extraites sont des suggestions.
Vous validez chaque élément avant utilisation.
Vous pouvez supprimer le fichier original après import.
```

Flux :

```txt
CV PDF local
↓
Extraction locale
↓
Suggestions de faits
↓
Validation utilisateur
↓
Base locale de faits validés
↓
Suppression optionnelle du fichier original
```

---

## 3. Architecture de développement actuelle

Pour l’instant, rester en environnement de développement :

```txt
Frontend Angular : http://localhost:4200
Backend Python : http://localhost:8000
Stockage : SQLite / fichiers locaux
```

Objectif actuel :

- tester les vrais usages ;
- valider le flux offre → CV → suivi ;
- vérifier que l’interface en 3 zones fonctionne ;
- vérifier que la preuve par les faits est compréhensible ;
- itérer sans créer trop tôt un installateur, une APK, une app iOS ou un cloud.

---

## 4. Architecture cible V1 locale

La meilleure V1 produit est une application locale desktop.

```txt
CVForge Desktop local
├── Angular buildé
├── Backend Python local
├── SQLite locale
├── Dossier local de fichiers
└── Extension navigateur optionnelle
```

Stockage recommandé :

```txt
CVForge/
  cvforge.db
  storage/
    proofs/
    exports/
    resumes/
    job_offers/
    backups/
```

SQLite stocke :

- offres ;
- candidatures ;
- statuts ;
- rappels ;
- contacts ;
- faits validés ;
- preuves ;
- CV générés ;
- messages ;
- pitchs ;
- historique.

Le dossier `storage/` contient :

- PDF ;
- captures ;
- documents ;
- exports ;
- fichiers importés ;
- preuves locales.

---

## 5. Modes possibles à long terme

### Mode 1 — Local strict

- aucun compte ;
- données sur l’appareil ;
- extension locale ;
- exports locaux ;
- sauvegarde ZIP.

### Mode 2 — Local + sauvegarde

- données locales ;
- export ZIP chiffré ;
- import sur un autre appareil ;
- sauvegarde manuelle.

### Mode 3 — Cloud optionnel

- compte utilisateur ;
- synchronisation PC / mobile ;
- partage temporaire ;
- notifications email / push ;
- usage multi-appareils.

Le cloud ne doit jamais être obligatoire.

---

## 6. Interface principale : atelier en trois zones

La vision principale de l’interface doit rester très simple :

```txt
[Offre d’emploi]  [Vue centrale active]  [Outils & assistance]
```

Métaphore à conserver :

```txt
CV = établi principal
Suivi = carnet de bord
Preuves = tiroir de justification
Outils avancés = placard avec les outils spécialisés
```

### Colonne gauche — Offre d’emploi

Elle affiche le contexte de l’offre active :

- titre ;
- entreprise ;
- source ;
- URL originale ;
- compétences demandées ;
- missions principales ;
- signaux faibles ;
- statut de l’offre ;
- actions rapides.

Actions :

- analyser l’offre ;
- ouvrir l’offre originale ;
- suivre cette offre ;
- ajouter au suivi ;
- archiver.

Le bouton “Envoyer à la forge” ne doit pas apparaître ici. Il est réservé à l’extension navigateur.

### Zone centrale — Vue active

La zone centrale est le cœur du travail.

Onglets possibles :

```txt
CV adapté | Message | Pitch | Suivi | Entretien | Preuves | Historique
```

Par défaut : `CV adapté`.

Quand l’utilisateur clique sur `Suivi`, le CV est remplacé temporairement par le tableau de suivi, sans changer de page et sans casser le cockpit.

### Colonne droite — Outils & assistance

Elle contient les outils contextuels :

- assistant IA ;
- banque de preuves ;
- rappels ;
- liens utiles ;
- outils avancés.

Les outils avancés, comme le simulateur ATS, doivent rester secondaires.

---

## 7. Bouton “Suivre cette offre”

CVForge doit proposer une action simple pour ajouter une offre à l’espace personnel de l’utilisateur.

Nom recommandé :

```txt
☆ Suivre cette offre
```

ou :

```txt
♡ Sauvegarder l’offre
```

Le bouton doit fonctionner comme un équivalent interne de l’extension navigateur.

Sources possibles de création d’une offre :

- bouton dans l’application ;
- extension navigateur ;
- ajout manuel d’URL ;
- futur partage mobile ;
- import depuis une liste d’offres.

Toutes ces entrées créent ou mettent à jour une entité `JobOffer`.

Statut initial recommandé :

```txt
Offre sauvegardée
```

Après sauvegarde, CVForge propose :

- analyser l’offre ;
- adapter le CV ;
- ajouter un rappel ;
- archiver.

---

## 8. Extension navigateur “Envoyer à la forge”

L’extension navigateur sert à capturer une offre depuis un job board.

Bouton :

```txt
Envoyer à la forge
```

Fonctionnement :

```txt
Job board
↓
Clic sur “Envoyer à la forge”
↓
Extension navigateur
↓
Envoi URL + titre + source vers CVForge local
↓
Stockage dans SQLite locale
```

Payload minimal :

```json
{
  "url": "https://www.apec.fr/...",
  "title": "Développeur Full Stack",
  "source": "apec",
  "domain": "apec.fr",
  "captured_at": "2026-05-04T15:45:00"
}
```

Règles :

- ne pas scraper massivement ;
- ne pas contourner de CAPTCHA ;
- ne pas capturer automatiquement tout le texte de l’offre ;
- ne pas collecter de données personnelles inutiles ;
- garder le lien original ;
- demander confirmation si l’utilisateur veut inclure le texte complet.

### Communication extension → application locale

Option V1 recommandée :

```txt
Extension navigateur
↓
http://127.0.0.1:8765/api/job-offers/bookmark
↓
CVForge Desktop local
```

Sécurité minimale :

- token local d’appairage ;
- CORS verrouillé ;
- refus si CVForge n’est pas lancé ;
- aucun accès externe.

---

## 9. Inspiration Blip : appairage multi-appareils

L’application Blip inspire une future fonctionnalité d’appairage entre appareils.

Idée CVForge :

```txt
Ajouter un appareil
```

Usage futur :

- le PC devient l’espace principal ;
- le téléphone devient un compagnon léger ;
- l’utilisateur peut envoyer une URL d’offre depuis le téléphone vers le PC ;
- l’appairage se fait par code ou QR code.

Flux possible :

```txt
PC CVForge
↓ affiche QR code
Mobile scanne
↓
Mobile peut envoyer une URL / note / rappel au PC
```

À ne pas développer avant la version desktop stable.

---

## 10. Stratégie mobile

Le mobile ne doit pas être prioritaire pour la production complète de candidature.

Le desktop reste prioritaire, car :

- éditer un CV sur téléphone est pénible ;
- vérifier des preuves demande de l’espace ;
- comparer offre / CV / outils est plus naturel sur grand écran ;
- postuler sérieusement se fait souvent sur PC.

Le mobile peut devenir un compagnon utile pour :

- sauvegarder une offre ;
- consulter une candidature ;
- changer un statut ;
- ajouter une note rapide ;
- voir un rappel ;
- lire un pitch avant entretien ;
- ouvrir un CV envoyé.

Stratégie recommandée :

```txt
V1 : Desktop / web local
V2 : Extension navigateur
V3 : Mobile compagnon léger
```

Principe :

```txt
Desktop first, mobile useful.
```

---

## 11. Rappels et notifications

### Objectif

CVForge doit aider l’utilisateur à ne pas oublier les actions importantes.

Cas d’usage :

- relancer une entreprise ;
- préparer un entretien ;
- envoyer un message de remerciement ;
- finaliser un CV avant une date limite ;
- revoir une offre sauvegardée ;
- mettre à jour un statut.

### Modèle de données proposé

```ts
Reminder {
  id: string;
  title: string;
  description?: string;
  due_at: string;
  type: "follow_up" | "interview" | "deadline" | "task" | "status_update";
  status: "pending" | "done" | "snoozed" | "cancelled";
  related_offer_id?: string;
  related_application_id?: string;
  notification_channels: string[];
  created_at: string;
  completed_at?: string;
}
```

### V1

- rappels in-app ;
- affichage dans le dashboard ;
- rappels liés à une candidature ;
- action “marquer comme fait”.

### V2

- notifications navigateur / PWA ;
- notifications desktop ;
- export calendrier `.ics`.

### V3

- email ;
- push mobile ;
- synchronisation Google Calendar / Outlook.

---

## 12. Suivi intelligent / tableau type Excel

### Précision importante

Le tableau de suivi ne doit pas être une page séparée qui sort l’utilisateur du contexte.

Il doit apparaître dans la zone centrale, à la place temporaire du CV, quand l’utilisateur clique sur l’onglet :

```txt
Suivi
```

La structure globale reste :

```txt
[Offre d’emploi]  [Suivi]  [Outils & assistance]
```

### Objectif

Permettre à l’utilisateur de piloter toutes ses candidatures :

- statuts ;
- rappels ;
- contacts ;
- emails ;
- téléphones ;
- relances ;
- notes ;
- documents envoyés ;
- dates ;
- prochaines actions.

### Champs recommandés

- date de création ;
- date de candidature ;
- entreprise ;
- intitulé ;
- source ;
- URL de l’offre ;
- statut ;
- priorité ;
- contact principal ;
- email du contact ;
- téléphone ;
- CV utilisé ;
- message envoyé ;
- date de relance ;
- prochain rappel ;
- notes ;
- décision finale.

### Statuts possibles

```txt
Offre sauvegardée
À analyser
CV à adapter
CV généré
Prêt à postuler
Postulé
Relance à faire
Relancé
Entretien prévu
Entretien passé
Test technique
En attente de retour
Refus
Accepté
Abandonné
Archivé
```

### Action “J’ai postulé ici”

Depuis une offre ou une candidature, ajouter une action :

```txt
J’ai postulé ici
```

Formulaire :

```txt
Date de candidature
CV utilisé
Message envoyé
Nom du contact
Email
Téléphone
Relance prévue
Notes
```

Après validation :

- statut = `Postulé` ;
- ajout au suivi ;
- proposition de rappel dans 7 jours.

### Historique des actions

Chaque candidature doit conserver un journal :

```txt
Offre sauvegardée le 18/05/2026
CV généré le 18/05/2026
Candidature envoyée le 19/05/2026
Relance prévue le 26/05/2026
Entretien prévu le 31/05/2026
```

---

## 13. Banque de preuves

La banque de preuves est centrale.

Elle doit être visible mais non envahissante.

Dans la colonne droite :

```txt
Banque de preuves
✓ Expérience URSSAF
✓ Projet Laravel / Angular
✓ Optimisation SQL
✓ API REST
+ Ajouter une preuve
Voir toutes les preuves
```

Objectifs :

- justifier les phrases du CV ;
- relier les compétences à des faits ;
- éviter l’invention ;
- aider l’utilisateur à préparer l’entretien ;
- alimenter le pitch et les réponses.

### Niveaux de visibilité

```ts
ProofVisibility = "private" | "anonymized" | "public" | "shareable";
```

Règles :

- une preuve privée ne doit jamais être partagée automatiquement ;
- une preuve anonymisée peut justifier une formulation publique ;
- une preuve publique peut être utilisée dans un dossier partagé ;
- l’utilisateur valide explicitement ce qui est partagé.

---

## 14. Projet professionnel guidé

Les documents d’accompagnement type “Agir pour l’emploi” montrent une logique utile :

```txt
Affirmation
↓
Comment je démontre cette affirmation
↓
Preuve
```

CVForge doit intégrer cette méthode dans “Mon parcours”.

Sections possibles :

- mes motivations ;
- mes savoir-faire ;
- mes savoir-être ;
- mes compétences naturelles ;
- mes contraintes ;
- mon offre de service ;
- mon slogan professionnel.

Exemple :

```txt
Affirmation :
Je sais accompagner et rendre service.

Comment je le démontre :
J’ai animé des formations internes pour aider des collègues non développeurs à comprendre les outils de développement.

Preuve :
Support de formation / expérience professionnelle / note personnelle.
```

Ce module aide à créer la base de faits avant même d’ajouter une offre.

---

## 15. Outils avancés et ATS

Le simulateur ATS doit rester dans les outils avancés.

Il ne doit pas envahir l’interface principale.

### Contrôles utiles

- structure compatible ATS ;
- mots-clés présents ;
- mots-clés absents ;
- longueur du CV ;
- sections lisibles ;
- phrases claires ;
- résultats quantifiés ;
- mise en forme lisible ;
- cohérence avec l’offre ;
- objections potentielles.

### Ne pas promettre un score magique

Éviter :

```txt
Votre CV passe les ATS à 92 %
```

Préférer :

```txt
Structure : claire
Mots-clés présents : 8 / 11
Compétences absentes : Kubernetes, AWS
Résumé : trop générique
Phrases : à rendre plus concrètes
```

### Checklist qualité inspirée des bonnes pratiques

CVForge peut vérifier :

1. structure claire ;
2. éléments forts du parcours ;
3. sélection des expériences à impact ;
4. résultats ou responsabilités quantifiés ;
5. mise en forme qui guide l’œil ;
6. phrases simples et percutantes ;
7. annonces représentatives de la cible ;
8. mots-clés aux bons endroits ;
9. objections anticipées.

Chaque suggestion doit rester factuelle.

---

## 16. Assistance IA

CVForge peut proposer de l’assistance IA tout en restant local-first.

### Niveaux possibles

```txt
Niveau 1 — Sans IA
Règles locales, mots-clés, matching, lisibilité.

Niveau 2 — IA locale
Ollama ou modèle local sur le PC.

Niveau 3 — IA cloud optionnelle
Uniquement avec consentement explicite.
```

### Règle

L’IA propose.  
CVForge vérifie.  
L’utilisateur valide.

L’IA ne doit jamais écrire directement dans le CV sans validation.

### Paramètres recommandés

```txt
Assistant IA :
○ Désactivé
● Local avec Ollama
○ Cloud avec confirmation
```

Pour le cloud :

- confirmer avant envoi ;
- sélectionner les données envoyées ;
- exclure les preuves privées par défaut ;
- afficher un historique des envois.

---

## 17. Préparation d’entretien

### Objectif

Aider l’utilisateur à défendre sa candidature après la postulation.

Ce module peut devenir un onglet central :

```txt
Entretien
```

Entrées :

- offre ;
- CV adapté ;
- preuves ;
- pitch ;
- informations publiques sur l’entreprise si l’utilisateur l’autorise.

Sorties :

- pitch 1 minute ;
- questions probables ;
- réponses suggérées ;
- exemples à raconter ;
- objections à anticiper ;
- questions à poser ;
- points à vérifier sur l’entreprise.

### Recherche entreprise

La recherche sur l’entreprise doit être optionnelle.

Flux :

```txt
Voulez-vous rechercher des informations publiques sur cette entreprise ?
↓
Recherche optionnelle
↓
Sources affichées
↓
Résumé vérifiable
```

Ne pas faire de recherche invisible.

### Anticipation des objections

Exemple :

```txt
Objection possible :
Vous avez peu d’expérience sur Kubernetes.

Réponse conseillée :
Ne pas prétendre maîtriser Kubernetes.
Mettre en avant Docker, la capacité d’apprentissage et les expériences prouvées liées au déploiement ou à la documentation.
```

---

## 18. Module Pitch

Le pitch doit être basé sur les faits validés.

Formats :

- pitch 30 secondes ;
- pitch 1 minute ;
- pitch 2 minutes ;
- pitch entretien ;
- pitch LinkedIn ;
- pitch reconversion ;
- réponse à “Présentez-vous”.

Évolutions futures :

- prompteur ;
- chronomètre ;
- répétition guidée ;
- enregistrement audio local ;
- enregistrement vidéo local ;
- partage sécurisé.

---

## 19. Liens utiles et ressources pratiques

Module simple pour centraliser des ressources :

- job boards ;
- formations ;
- préparation entretien ;
- modèles de messages ;
- démarches administratives ;
- droits et aides ;
- ressources métier ;
- événements ;
- outils CV ;
- articles de veille.

Lien avec les compétences manquantes :

```txt
Compétence absente : Kubernetes
Action CV : ne pas ajouter
Action progression : ajouter à “à apprendre”
Ressources : formations Kubernetes débutant
```

---

## 20. Partage optionnel à un observateur

Fonctionnalité facultative :

```txt
Demander un avis
```

L’utilisateur peut partager une candidature avec :

- un ami recruteur ;
- un RH ;
- un ancien manager ;
- un mentor ;
- un formateur ;
- une personne de confiance ;
- un conseiller emploi si souhaité.

### Règles

L’utilisateur choisit ce qu’il partage.

Ne jamais partager par défaut :

- preuves privées ;
- notes personnelles ;
- historique complet ;
- autres offres ;
- données sensibles ;
- documents non validés.

### V1

Export local d’un dossier de relecture :

- CV adapté ;
- message court ;
- résumé de l’offre ;
- pitch ;
- points forts ;
- questions à poser.

### V2

Lien temporaire :

- expiration ;
- lecture seule ;
- révocation ;
- contenu limité.

### V3

Commentaires externes.

L’observateur ne modifie jamais directement les documents.

---

## 21. Multilingue et conventions pays

Le multilingue doit être prévu, mais pas prioritaire.

Il ne s’agit pas seulement de traduire.

Il faut gérer :

- langue de l’interface ;
- langue du CV ;
- pays cible ;
- conventions locales ;
- format de date ;
- style attendu ;
- rubriques à inclure ou éviter.

V1 :

```txt
Français uniquement
```

V2 :

```txt
Français + anglais
```

Plus tard :

- espagnol ;
- allemand ;
- portugais ;
- italien ;
- conventions par pays.

---

## 22. Roadmap recommandée

### Phase actuelle — Dev local

- Angular 4200 ;
- backend Python local ;
- SQLite / fichiers ;
- tests d’usage ;
- interface 3 zones ;
- suivi simple ;
- preuves ;
- rappels in-app.

### V1 — Prototype utilisable local

- ajout manuel d’offre ;
- sauvegarde / suivi d’offre ;
- analyse offre ;
- CV adapté ;
- message court ;
- banque de preuves visible ;
- suivi intelligent ;
- rappels in-app ;
- exports simples.

### V2 — Desktop local

- packaging desktop ;
- Angular buildé ;
- backend embarqué ;
- SQLite locale ;
- stockage local ;
- lancement simple.

### V3 — Extension navigateur

- bouton “Envoyer à la forge” ;
- envoi URL + titre + source ;
- appairage local ;
- stockage dans CVForge.

### V4 — Assistance avancée

- IA locale ;
- checklist qualité CV ;
- préparation entretien ;
- pitch ;
- outils avancés ;
- exports propres.

### V5 — Mobile compagnon

- sauvegarder une offre depuis mobile ;
- consulter suivi ;
- rappels ;
- notes rapides ;
- pitch entretien ;
- appairage type Blip.

### V6 — Cloud optionnel

- synchronisation multi-appareils ;
- partage observateur ;
- notifications email / push ;
- compte utilisateur optionnel.

---

## 23. Principe final

CVForge doit rester :

```txt
Simple en surface.
Solide en profondeur.
Local-first par défaut.
Contrôlé par l’utilisateur.
Basé sur des faits.
Utile avant d’être spectaculaire.
```

Question permanente :

> Est-ce que cette fonctionnalité aide vraiment le candidat à mieux postuler, mieux se préparer ou mieux suivre ses démarches ?

Si non : la repousser.


---

# ADDENDUM V2 — Organisation ergonomique cockpit et nouvelles décisions

## 0. Décision centrale

Le CV est l’objet principal affiché par défaut, mais le vrai centre fonctionnel de CVForge est la **candidature active**.

Une candidature active regroupe :

```txt
Offre active
+ CV adapté
+ message ou lettre
+ preuves associées
+ statut
+ prochaine action
+ rappels
+ historique
```

Le CV reste l’établi principal, mais il ne doit pas absorber toute l’application. CVForge ne doit pas devenir un simple générateur de CV entouré de boutons. Le produit doit rester un cockpit de candidature.

Phrase directrice :

```txt
CVForge n’est pas une suite de pages.
CVForge est un cockpit : une offre à gauche, un document ou un suivi au centre, des preuves et outils à droite, avec un tableau de bord pour savoir quoi faire aujourd’hui.
```

---

# 24. Architecture ergonomique en trois niveaux

## Niveau 1 — Tableau de bord

Objectif : savoir quoi faire aujourd’hui.

Le tableau de bord est la page d’accueil opérationnelle de CVForge. Il ne remplace pas le suivi complet, mais il agrège les actions importantes.

Il affiche :

- relances à faire ;
- candidatures sans réponse ;
- offres sauvegardées à analyser ;
- CV à finaliser ;
- entretiens à préparer ;
- prochaines échéances ;
- tâches en retard ;
- statistiques simples ;
- actions rapides.

Exemple :

```txt
Aujourd’hui

- 2 relances à faire
- 1 entretien à préparer
- 3 offres sauvegardées à analyser
- 1 CV adapté à finaliser
```

Actions rapides :

```txt
Ajouter une offre
Analyser une offre
Voir mes relances
Préparer un entretien
Ouvrir le suivi
```

## Niveau 2 — Atelier de candidature

Objectif : travailler sur une offre précise.

L’atelier est le cœur de l’application.

Structure :

```txt
[Colonne gauche : Offre active]
[Centre : CV / Message / Pitch / Suivi / Entretien]
[Colonne droite : Preuves / Assistant / ATS / Rappels / Notes]
```

L’utilisateur reste dans un contexte stable. Il peut passer du CV au message, au pitch, au suivi ou à l’entretien sans perdre l’offre active.

## Niveau 3 — Bases personnelles

Objectif : gérer les données de fond.

Sections dédiées :

```txt
Profil maître
Projet cible
Bibliothèque
Paramètres
```

Ces sections ne doivent pas être de simples tiroirs, car elles contiennent des données structurantes. Elles alimentent l’atelier et le tableau de bord.

---

# 25. Navigation principale recommandée

Navigation principale :

```txt
Tableau de bord
Atelier
Suivi
Profil maître
Projet cible
Bibliothèque
Paramètres
```

## Rôle de chaque section

### Tableau de bord

```txt
Que dois-je faire aujourd’hui ?
```

Contient :

- rappels ;
- prochaines actions ;
- entretiens ;
- relances ;
- offres à traiter ;
- synthèse rapide.

### Atelier

```txt
Je travaille sur une candidature précise.
```

Contient :

- offre active ;
- CV adapté ;
- message ;
- pitch ;
- entretien ;
- preuves ;
- outils.

### Suivi

```txt
Je pilote toutes mes candidatures.
```

Contient :

- tableau de suivi ;
- statuts ;
- relances ;
- contacts ;
- documents envoyés ;
- historique ;
- filtres ;
- vues alternatives.

### Profil maître

```txt
Je structure mon parcours.
```

Contient :

- expériences ;
- compétences ;
- projets ;
- formations ;
- certifications ;
- faits validés ;
- preuves associées.

### Projet cible

```txt
Je définis ce que je veux vraiment.
```

Contient :

- métiers visés ;
- secteurs ;
- salaire cible ;
- télétravail ;
- mobilité ;
- contraintes ;
- valeurs ;
- critères non négociables ;
- priorités.

### Bibliothèque

```txt
Je retrouve mes documents et preuves.
```

Contient :

- preuves ;
- CV générés ;
- messages ;
- pitchs ;
- exports ;
- fichiers sources ;
- captures ;
- documents utiles.

### Paramètres

```txt
Je contrôle mes données et mes préférences.
```

Contient :

- stockage local ;
- IA activée ou non ;
- modèle local / cloud ;
- confidentialité ;
- exports ;
- sauvegarde ;
- extension navigateur ;
- appairage futur.

---

# 26. Placement définitif des 6 modules principaux

## 1. Profil maître

Le profil maître est la base du système.

Il ne doit pas être réduit à un simple CV.

Il contient :

```txt
Expériences
Compétences
Projets
Formations
Certifications
Faits validés
Preuves
Versions de CV
```

Le CV adapté est une sortie générée depuis le profil maître, pas la source de vérité.

Placement recommandé :

```txt
Page dédiée : Profil maître / Mon parcours
Vue centrale dans l’atelier : CV adapté
Colonne droite : preuves liées au CV
```

## 2. Projet professionnel

Le projet professionnel définit le cap.

Il contient :

```txt
Métiers ciblés
Secteurs ciblés
Types d’entreprises
Télétravail souhaité
Salaire cible
Localisation
Valeurs
Contraintes
Critères non négociables
Priorités
Ce que je veux éviter
```

Placement recommandé :

```txt
Page dédiée : Projet cible / Mon cap
Résumé contextuel possible dans la colonne droite
Utilisé automatiquement pour le scoring des offres
```

Ce module ne doit pas être un simple tiroir. Il est trop important pour cela.

Il influence :

- analyse d’offre ;
- score de compatibilité ;
- points de vigilance ;
- priorisation des candidatures ;
- recommandations de relance ;
- pertinence des métiers explorés.

Exemple d’usage :

```txt
Point de vigilance :
L’offre demande 4 jours sur site, alors que votre projet cible indique une préférence forte pour le télétravail.
```

## 3. Analyse de l’offre

L’analyse de l’offre doit rester rapidement visible à côté du CV.

Placement recommandé :

```txt
Colonne gauche de l’atelier
```

La colonne gauche affiche :

```txt
Titre du poste
Entreprise
Source
URL originale
Statut de l’offre
Compétences demandées
Missions principales
Mots-clés
Contraintes
Niveau attendu
Score de compatibilité
Points de vigilance
Actions rapides
```

Actions :

```txt
Analyser l’offre
Adapter le CV
Sauvegarder l’offre
J’ai postulé ici
Archiver
Ouvrir l’offre originale
```

Si aucune offre n’est active :

```txt
Ajoutez une offre
Collez une description
Importez une URL
Envoyer à la forge depuis l’extension
```

## 4. Outils, preuves, ATS, assistance IA

Les outils doivent être à droite du CV, mais ils doivent rester contextuels.

Placement recommandé :

```txt
Colonne droite de l’atelier
```

La colonne droite n’est pas un fourre-tout. Elle change selon la vue centrale.

Si la vue centrale est le CV :

```txt
Preuves liées
Suggestions de formulation
Qualité / ATS
Mots-clés manquants
Versions
Export
```

Si la vue centrale est le message :

```txt
Ton du message
Preuves utiles
Arguments courts
Contact recruteur
```

Si la vue centrale est le pitch :

```txt
Preuves à raconter
Questions probables
Objections à anticiper
Chronomètre
```

Si la vue centrale est le suivi :

```txt
Rappels
Actions en retard
Contacts
Notes rapides
```

Onglets possibles de la colonne droite :

```txt
Preuves
Assistant
Qualité
Rappels
Notes
```

## 5. Suivi intelligent

Le suivi est le tableau Excel amélioré.

Il doit exister sous deux formes :

```txt
Suivi global : page dédiée
Suivi contextuel : onglet central dans l’atelier
```

### Suivi global

Accessible depuis la navigation principale.

Il permet de piloter toutes les candidatures.

Vues possibles :

```txt
Tableau
Kanban
Calendrier
Relances
```

V1 recommandée :

```txt
Vue tableau
Filtres
Statuts
Prochaine action
Date de relance
```

### Suivi contextuel

Dans l’atelier, l’utilisateur peut cliquer sur l’onglet :

```txt
Suivi
```

Le centre remplace temporairement le CV par le suivi de la candidature active.

La structure reste :

```txt
[Offre active] [Suivi de cette candidature] [Rappels / Notes / Contacts]
```

Le suivi ne doit pas être un tiroir latéral, car un tableau a besoin d’espace.

## 6. Centre de contrôle / rappels

Les rappels ne doivent pas être enfermés uniquement dans le suivi.

Ils doivent exister à trois niveaux :

```txt
1. Dans le suivi : prochaine action par candidature.
2. Dans la colonne droite : rappel contextuel lié à l’offre active.
3. Dans le tableau de bord : synthèse des actions du jour.
```

Le module de contrôle est donc plutôt :

```txt
Tableau de bord
```

Il affiche :

- actions du jour ;
- relances ;
- entretiens ;
- tâches en retard ;
- offres à analyser ;
- échéances.

Il ne doit pas être seulement une page “Rappels”.

---

# 27. Règles d’usage des tiroirs

## À quoi servent les tiroirs ?

Les tiroirs latéraux servent à consulter rapidement une information sans quitter le contexte.

Utiliser un tiroir pour :

```txt
Détail rapide d’une preuve
Note rapide
Contact recruteur
Rappel
Mini historique
Détail rapide d’une offre
Aperçu d’un document
```

## Ce qui ne doit pas être un tiroir

Ne pas mettre en tiroir principal :

```txt
Profil maître complet
Projet professionnel complet
Suivi global
Tableau de candidatures complet
Bibliothèque complète
Paramètres complets
```

Ces éléments doivent être des pages ou vues dédiées.

## Règle simple

```txt
Tiroir = consulter / piocher / compléter rapidement.
Centre = travailler.
Page dédiée = structurer durablement.
```

---

# 28. Flux utilisateur principal révisé

Flux recommandé :

```txt
1. L’utilisateur remplit son profil maître.
2. L’utilisateur définit son projet cible.
3. L’utilisateur ajoute une offre.
4. L’offre apparaît dans la colonne gauche.
5. CVForge analyse l’offre.
6. Le CV adapté apparaît au centre.
7. Les preuves et suggestions apparaissent à droite.
8. L’utilisateur valide les formulations.
9. L’utilisateur génère un message court.
10. L’utilisateur clique sur “J’ai postulé ici”.
11. La candidature est ajoutée au suivi.
12. CVForge propose une relance dans 5 à 7 jours.
13. Le tableau de bord rappelle l’action au bon moment.
14. L’utilisateur prépare l’entretien depuis l’atelier si besoin.
```

---

# 29. Scoring d’opportunité

CVForge peut comparer une offre avec :

```txt
Profil maître
Projet cible
Critères non négociables
Compétences disponibles
Preuves
```

Scores possibles :

```txt
Compatibilité compétences : 0 à 5
Compatibilité projet : 0 à 5
Compatibilité contraintes : 0 à 5
Intérêt personnel : 0 à 5
Effort de candidature : faible / moyen / fort
Priorité : haute / moyenne / basse
```

Exemples :

```txt
Score global : 18/25
Recommandation : postuler en priorité.
```

```txt
Score global : 9/25
Recommandation : garder en veille, mais ne pas prioriser.
```

Important :

Ne pas transformer ce scoring en vérité absolue.

Formulation recommandée :

```txt
Aide à la décision
```

et non :

```txt
Verdict automatique
```

---

# 30. Priorités MVP mises à jour

## MVP indispensable

```txt
Profil maître
Projet cible simple
Ajout manuel d’offre
Analyse simple de l’offre
Vue atelier en 3 zones
CV adapté
Message court
Sauvegarde candidature
Suivi tableau
Rappels in-app
Banque de preuves simple
Export CV / message
```

## MVP enrichi

```txt
Scoring opportunité
Pitch
Préparation entretien
Historique actions
Vue tableau améliorée
Filtres candidatures
Export CSV
Extension navigateur minimale
```

## À repousser

```txt
Cloud
Mobile complet
IA cloud par défaut
Scraping massif
Abonnement complexe
Partage externe avancé
Synchronisation multi-appareils
```

---

# 31. Ce qu’il ne faut pas faire maintenant

Ne pas transformer CVForge en :

```txt
ERP complet de recherche d’emploi
CRM RH
ATS magique
réseau social
cloud obligatoire
générateur automatique incontrôlé
plateforme de scraping d’offres
```

Ne pas tout mettre en tiroirs.

Ne pas créer une page isolée pour chaque micro-fonction.

Ne pas faire dépendre le produit d’une IA cloud.

Ne pas écrire automatiquement dans le CV sans validation.

Ne pas masquer les preuves et les faits.

---

# 32. Résumé final V2

CVForge doit rester :

```txt
Simple en surface.
Solide en profondeur.
Local-first par défaut.
Contrôlé par l’utilisateur.
Basé sur des faits.
Utile avant d’être spectaculaire.
```

Question permanente :

```txt
Est-ce que cette fonctionnalité aide vraiment le candidat à mieux postuler, mieux se préparer ou mieux suivre ses démarches ?
```

Si non : repousser.

---

# ADDENDUM V3 — Décision UI après comparaison des maquettes

## 1. Décision principale

La maquette 3 devient la référence principale pour l’interface réelle de CVForge.

La maquette 1 reste utile comme schéma conceptuel pour expliquer les grands modules :

- profil maître ;
- projet professionnel ;
- analyse de l’offre ;
- outils et ressources ;
- suivi des candidatures ;
- rappels et actions.

Mais l’interface réellement utilisée par l’utilisateur doit se rapprocher de la maquette 3, car elle est plus lisible, plus naturelle et plus proche d’une application professionnelle.

Décision :

```txt
Maquette 1 = carte conceptuelle / documentation / onboarding.
Maquette 2 = prototype intermédiaire.
Maquette 3 = nouvelle référence UI.

## Source de vérité visuelle

La maquette de référence pour l’interface principale est :

```txt
docs/maquettes/cv-forge_maquette3.png