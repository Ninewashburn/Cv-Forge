/** Types partagés, alignés sur les enums Pydantic du backend. */

export type FactType = 'experience' | 'skill' | 'project' | 'education' | 'achievement';
export type ProofType = 'note' | 'link' | 'document';
export type Confidentiality = 'private' | 'anonymized' | 'public';
export type SentenceStatus = 'valid' | 'rejected';
export type VariantStatus = 'draft' | 'validated';
export type ApplicationStatus = 'envoyee' | 'reponse' | 'entretien' | 'refus';
export type PromptKind = 'adapter' | 'auditer' | 'muscler' | 'accrocher';

/** Champs sync-ready présents sur toutes les entités lues (UUID, timestamps, soft delete). */
export interface Timestamped {
  readonly id: string;
  readonly created_at: string;
  readonly updated_at: string;
  readonly deleted_at: string | null;
}
