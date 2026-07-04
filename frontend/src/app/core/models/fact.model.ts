import { FactType, Timestamped } from './common.model';

export interface Fact extends Timestamped {
  profile_id: string;
  type: FactType;
  title: string;
  content: string;
  tags: string[];
  validated: boolean;
  position: number;
  proof_ids: string[];
}

export interface FactCreate {
  type: FactType;
  title: string;
  content?: string;
  tags?: string[];
  validated?: boolean;
  position?: number;
  /** Absent → rattaché au profil maître (V1 : un seul profil). */
  profile_id?: string | null;
}

export interface FactUpdate {
  type?: FactType;
  title?: string;
  content?: string;
  tags?: string[];
  validated?: boolean;
  position?: number;
}
