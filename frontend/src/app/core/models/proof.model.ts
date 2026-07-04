import { Confidentiality, ProofType, Timestamped } from './common.model';

export interface Proof extends Timestamped {
  type: ProofType;
  title: string;
  content: string;
  confidentiality: Confidentiality;
  file_name: string | null;
  fact_ids: string[];
}

export interface ProofCreate {
  type: ProofType;
  title: string;
  content?: string;
  confidentiality?: Confidentiality;
  fact_ids?: string[];
}

export interface ProofUpdate {
  type?: ProofType;
  title?: string;
  content?: string;
  confidentiality?: Confidentiality;
  fact_ids?: string[];
}
