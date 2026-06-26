# Instructions pour le développement de CVForge

Ce fichier agit comme une **charte de développement** pour guider la conception
du projet CVForge. Il résume les principes, les règles et les priorités que
l'équipe de développement (ou Codex) doit respecter.

## Principes fondateurs

- **Local-first et privacy-first :** toutes les données doivent pouvoir être
  traitées et stockées localement. Aucune donnée n'est envoyée automatiquement
  vers un service cloud sans le consentement explicite de l'utilisateur.
- **Anti-hallucination :** le système ne doit jamais inventer d'informations.
  Chaque phrase générée doit être reliée à un ou plusieurs faits validés
  (`source_fact_ids`) et, si possible, à des preuves (`source_proof_ids`). Les
  compétences ou expériences absentes de la base de faits doivent être
  clairement identifiées comme telles et ne pas apparaître dans les documents
  générés.
- **Modularité :** l'application doit être organisée en modules distincts
  (analyse, matching, génération, validation) afin de faciliter l'évolution et
  les tests.
- **Évolutivité métier :** bien que le MVP cible les développeurs fullstack, le
  modèle de données ne doit pas être limité à une discipline spécifique. Les
  entités `FactItem` et `ProofItem` doivent pouvoir décrire n'importe quel type
  de parcours professionnel.

## Modules du MVP

1. **CV maître structuré** : gestion des faits (expériences, compétences,
   projets, formations) avec leurs tags et preuves associées.
2. **Banque de preuves** : stockage de notes, liens ou documents anonymisés
   justifiant les faits.
3. **Analyse d'offre** : extraction de compétences et missions à partir d'un
   texte d'offre d'emploi. L'algorithme peut rester simple au départ
   (keywords), mais doit être conçu pour intégrer ultérieurement des modèles NLP
   plus avancés.
4. **Génération contrôlée** : création d'un CV adapté et d'un message court en
   sélectionnant uniquement des faits validés. Chaque élément généré doit être
   tracé.

## Exclusions pour le MVP

- Pas d'interface graphique complète (Angular n'est qu'un squelette).
- Pas d'API REST (FastAPI viendra plus tard).
- Pas d'IA externe (Ollama, Llama) dans la version initiale.
- Pas de suivi de candidature ni d'extension navigateur à ce stade.
- Pas de multilingue (uniquement français).
- Pas de dépendance à Canva ou autres outils fermés.

## Règles techniques

- Respecter l'architecture **Extract → Transform → Validate → Load**.
- Séparer la logique métier du stockage et de l'interface.
- Prévoir une persistance locale (SQLite) pour les profils et offres.
- Préparer le code à recevoir une API REST (mais ne pas l'implémenter dans le
  MVP).
- Écrire des tests unitaires pour les modules critiques (matching, validation).
- Utiliser des structures de données claires et documentées.

## Conseils de développement

- **Commencer petit :** implémenter un moteur CLI simple avant de s'engager
  dans une interface complète.
- **Valider les données :** toujours vérifier qu'une phrase ou une compétence a
  au moins une source. Ajouter une alerte sinon.
- **Documenter :** mettre à jour la documentation (`docs/`) à chaque évolution
  majeure du modèle ou des règles.
- **Simplicité :** préférer des solutions simples et lisibles aux optimisations
  prématurées.

Ce fichier doit être consulté régulièrement pendant le développement afin de
garantir que toutes les contributions respectent la vision du projet.
