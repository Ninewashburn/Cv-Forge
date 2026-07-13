/** Jeux d'exemple pour tester le parcours (portés de CVForge Lite). */

export interface Sample {
  offer: string;
  cv: string;
  linkedin: string;
}

export type SampleKind = 'dev' | 'gestion';

export const SAMPLES: Record<SampleKind, Sample> = {
  dev: {
    offer: `Développeur Fullstack Angular / Spring Boot (H/F) - CDI, Caen
Nous recherchons un développeur fullstack pour renforcer notre équipe produit.

Vos missions :
- Développer de nouvelles fonctionnalités en Angular et TypeScript
- Concevoir des API en Spring Boot avec PostgreSQL
- Écrire des tests unitaires et participer aux revues de code
- Déployer avec Docker, Kubernetes et GitLab CI

Profil :
- Vous maîtrisez Angular, Spring Boot et PostgreSQL
- Vous connaissez Docker ; Kubernetes est un plus
- Vous travaillez en méthode agile Scrum
Angular et Spring Boot sont au coeur de notre stack.`,
    cv: `Lina Carvalho - Développeuse Fullstack
Caen · lina.carvalho@mail.fr · github.com/linacarvalho

EXPÉRIENCE
Développeuse fullstack - Atelier Numérique (2023-2026)
- Développement d'un dashboard de supervision en Angular et TypeScript
- API REST en Spring Boot, base PostgreSQL, conteneurisation Docker
- Tests unitaires (JUnit, Jasmine), revues de code, méthode Scrum

Développeuse junior - WebFabrik (2022-2023)
- Sites e-commerce, intégration responsive, corrections de bugs

FORMATION
Titre professionnel Concepteur Développeur d'Applications (2022)`,
    linkedin: `Lina Carvalho
Développeuse Fullstack · Caen

Expérience
Développeuse fullstack - Atelier Numérique (2023 - aujourd'hui)
Angular, TypeScript, Spring Boot et PostgreSQL au quotidien. Mise en place du
déploiement continu avec GitLab CI/CD et orchestration des conteneurs sous Kubernetes.

Compétences
Angular · TypeScript · Spring Boot · PostgreSQL · Docker · Kubernetes · GitLab CI/CD · Scrum`,
  },
  gestion: {
    offer: `Assistant administratif et commercial (H/F) - CDI, Rouen
PME du secteur logistique, nous recherchons un assistant polyvalent.

Vos missions :
- Facturation et établissement des devis clients
- Relances des impayés et suivi des règlements
- Mise à jour du CRM et des tableaux de bord Excel (tableaux croisés dynamiques)
- Accueil téléphonique, gestion des plannings

Profil :
- Vous maîtrisez Excel et les tableaux croisés dynamiques
- Une première expérience en facturation est exigée
- La connaissance d'un CRM et d'un ERP est un plus`,
    cv: `Karim Bensaïd - Assistant de gestion
Rouen · k.bensaid@mail.fr

EXPÉRIENCE
Assistant de gestion - Transports Lemaire (2021-2026)
- Facturation clients et fournisseurs, établissement des devis
- Relances clients et suivi des règlements
- Saisie comptable dans l'ERP Sage, rapprochements bancaires
- Accueil téléphonique et gestion du courrier

FORMATION
BTS Gestion de la PME (2019)`,
    linkedin: `Karim Bensaïd
Assistant de gestion · Rouen

Expérience
Assistant de gestion - Transports Lemaire (2021 - aujourd'hui)
Facturation, devis et relances clients. Gestion d'un CRM (HubSpot) pour le suivi
commercial. Reporting via tableaux croisés dynamiques sous Excel. Élaboration des
plannings de tournées.

Compétences
Facturation · Devis · Relances · Sage · CRM HubSpot · Excel · Tableaux croisés dynamiques · Plannings`,
  },
};
