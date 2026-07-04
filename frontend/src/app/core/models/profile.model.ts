import { Timestamped } from './common.model';

export interface MasterProfile extends Timestamped {
  full_name: string;
  headline: string;
  email: string;
  phone: string;
  location: string;
  links: string[];
  summary: string;
  raw_import_text: string | null;
}

export interface MasterProfileUpdate {
  full_name?: string;
  headline?: string;
  email?: string;
  phone?: string;
  location?: string;
  links?: string[];
  summary?: string;
  raw_import_text?: string | null;
}
