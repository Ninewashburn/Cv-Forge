import { Timestamped } from './common.model';

/** Mot-clé pondéré : [terme, fréquence] — format renvoyé par l'analyse. */
export type WeightedKeyword = [string, number];

export interface Offer extends Timestamped {
  title: string;
  company: string;
  raw_text: string;
  source_url: string | null;
  keywords: WeightedKeyword[];
  required_skills: string[];
  optional_skills: string[];
  responsibilities: string[];
}

export interface OfferCreate {
  /** Import V1 : texte collé uniquement. L'URL n'est qu'une référence, jamais fetchée. */
  raw_text: string;
  title?: string;
  company?: string;
  source_url?: string | null;
}

export interface OfferUpdate {
  title?: string;
  company?: string;
  source_url?: string | null;
  raw_text?: string;
}
