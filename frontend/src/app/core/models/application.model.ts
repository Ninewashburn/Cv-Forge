import { ApplicationStatus, Timestamped } from './common.model';

/** Micro-suivi : une candidature exportée, son statut en 3 clics max. */
export interface Application extends Timestamped {
  offer_id: string;
  variant_id: string | null;
  status: ApplicationStatus;
  sent_at: string;
  notes: string;
}

export interface ApplicationCreate {
  offer_id: string;
  variant_id?: string | null;
  notes?: string;
}

export interface ApplicationUpdate {
  status?: ApplicationStatus;
  notes?: string;
}
