# Modèle de données

Le cœur de CVForge repose sur un modèle de données structuré qui permet de
relier chaque information générée à des faits et des preuves. Ce fichier décrit
les principales classes utilisées dans le moteur.

## FactItem

Représente un fait validé sur le parcours de l'utilisateur. Un fait peut être :

- une expérience professionnelle ;
- une compétence technique ou transversale ;
- un projet réalisé ;
- une formation ou certification ;
- un résultat ou une réalisation mesurable.

Champs :

- `id` : identifiant unique du fait ;
- `type` : type de fait (`experience`, `skill`, `project`, etc.) ;
- `title` : titre ou nom du fait ;
- `content` : description détaillée ;
- `tags` : liste de mots-clés liés au fait ;
- `validated` : booléen indiquant si le fait a été validé ;
- `proof_ids` : liste d'identifiants de `ProofItem` justifiant ce fait.

## ProofItem

Représente une preuve liée à un ou plusieurs faits. Une preuve peut être :

- une note personnelle ou une capture d'écran anonymisée ;
- un lien vers un dépôt GitHub, un ticket Jira ou un document technique ;
- un fichier de certification.

Champs :

- `id` : identifiant unique de la preuve ;
- `type` : type de preuve (`note`, `link`, `document`, etc.) ;
- `title` : titre de la preuve ;
- `content` : texte ou description de la preuve ;
- `confidentiality` : niveau de confidentialité (`private`, `anonymized`,
  `public`) ;
- `linked_fact_ids` : identifiants des faits supportés par cette preuve.

## JobOfferAnalysis

Représente l'extraction structurée d'une offre d'emploi.

Champs :

- `title` : titre du poste ;
- `company` : nom de l'entreprise (facultatif) ;
- `required_skills` : compétences obligatoires extraites ;
- `optional_skills` : compétences recommandées ;
- `responsibilities` : phrases décrivant les missions ;
- `weak_signals` : signaux faibles ou soft skills implicites.

## GeneratedSentence

Représente une phrase générée dans le CV adapté ou dans le message court.
Chaque phrase doit contenir des références aux faits qui la justifient.

Champs :

- `text` : texte de la phrase générée ;
- `source_fact_ids` : identifiants des faits utilisés pour générer cette
  phrase ;
- `source_proof_ids` : identifiants des preuves associées ;
- `status` : indique si la phrase est `valid` ou `rejected` après validation ;
- `reason` : explication pour laquelle la phrase a été rejetée.

## CVVariant (prévu)

Une entité `CVVariant` (à implémenter dans une prochaine phase) représentera
une version complète de CV générée pour une offre spécifique. Elle référencera :

- l'identifiant du profil maître utilisé ;
- l'identifiant de l'offre analysée ;
- la liste des `GeneratedSentence` ;
- les informations d'en-tête (titre, résumé) ;
- d'éventuelles métadonnées (score de correspondance, timestamp).

## ApplicationRecord (prévu)

Une entité `ApplicationRecord` permettra de suivre chaque candidature envoyée :

- l'offre ciblée ;
- la variante de CV utilisée ;
- le message de motivation envoyé ;
- la date et l'heure d'envoi ;
- le statut (à analyser, prêt, postulé, relance, entretien, refus, accepté) ;
- la planification de relance ;
- des notes d'entretien.

Ces entités supplémentaires seront intégrées dans le modèle de données plus
tard, lors de l'ajout du suivi de candidature et de l'interface utilisateur
complète.
