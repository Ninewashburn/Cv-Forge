# Périmètre du MVP

Le **MVP CVForge** a pour ambition de démontrer la valeur de l'approche ETVL
(Extract → Transform → Validate → Load) appliquée aux candidatures sans
développer d'emblée toute la profondeur du produit.

## Modules clés

1. **CV maître structuré**

   - Permet de créer et stocker des faits (expériences, compétences, projets,
     formations, langues, soft skills). Chaque fait est identifié par un `id`,
     typé et associé à des tags.
   - Les utilisateurs peuvent marquer les faits comme validés et lier des
     preuves via des identifiants de preuve.

2. **Banque de preuves**

   - Permet de stocker des notes, des liens, des captures ou des documents
     anonymisés liés à des faits.
   - Les preuves ont un niveau de confidentialité (privé, anonymisé, public) et
     servent à justifier les faits.

3. **Analyse d'offre**

   - L'utilisateur colle ou importe le texte d'une offre d'emploi.
   - L'analyse extrait des compétences, responsabilités, niveaux et signaux
     faibles (mots ou expressions suggérant des qualités ou contraintes
     implicites).
   - L'analyse produit une liste de compétences requises et une liste de
     compétences manquantes par rapport au profil.

4. **Génération contrôlée**

   - Génère un CV adapté à l'offre en ne sélectionnant que des faits validés.
   - Formule un titre, un résumé et des phrases d'expérience en associant à
     chaque phrase les `source_fact_ids` et `source_proof_ids` correspondants.
   - Produit un message court de candidature (mail ou LinkedIn) avec des
     références aux mêmes sources.

5. **Bookmarks d'offres**

   - Permet de sauvegarder localement les métadonnées minimales d'une offre
     consultée dans le navigateur.
   - Reçoit les offres via une API locale destinée à une extension navigateur.
   - Permet de filtrer les offres par source et par statut sans stocker le
     contenu complet des annonces.

6. **Centre de veille candidature**

   - Centralise offres, formations, news, événements et candidatures en cours.
   - Fonctionne comme un cockpit personnel local-first, pas comme un clone de
     job board.
   - Relie progressivement les compétences manquantes aux formations ou
     ressources de veille suivies par l'utilisateur.

## Fonctionnalités exclues du MVP

- Interface graphique complète (Angular n'est qu'un squelette).
- API REST (FastAPI sera ajoutée ultérieurement).
- IA locale pour l'analyse ou la reformulation (Ollama).
- Suivi de candidature détaillé (présenté dans la vision produit mais
  implémenté plus tard).
- Support multilingue (uniquement français pour la V1).
- Extension navigateur (phase ultérieure).
- Export vers Word/HTML/Canva (seulement PDF via RenderCV dans une version
  future).

## Livrables du MVP

- Un moteur Python exécutable en ligne de commande capable de lire un profil
  JSON, un fichier de preuves et un texte d'offre puis de générer un fichier
  JSON avec :
  - l'analyse de l'offre ;
  - les compétences correspondantes et manquantes ;
  - une variante de CV adaptée avec les sources ;
  - la liste des avertissements de validation.

Ce périmètre permet de valider les concepts de base, la fiabilité des
informations et la structure de données avant d'ajouter des couches
d'interface et d'IA.
