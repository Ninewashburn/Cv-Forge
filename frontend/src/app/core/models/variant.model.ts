import { SentenceStatus, Timestamped, VariantStatus } from './common.model';

/** Phrase générée, tracée jusqu'aux faits et preuves qui la justifient. */
export interface GeneratedSentence extends Timestamped {
  variant_id: string;
  text: string;
  source_fact_ids: string[];
  source_proof_ids: string[];
  status: SentenceStatus;
  reason: string | null;
  position: number;
}

export interface CvVariant extends Timestamped {
  profile_id: string;
  offer_id: string;
  recommended_title: string;
  recommended_summary: string;
  adapted_text: string;
  match_score: number | null;
  status: VariantStatus;
  sentences: GeneratedSentence[];
}

export interface CvVariantUpdate {
  recommended_title?: string;
  recommended_summary?: string;
  adapted_text?: string;
  status?: VariantStatus;
}
