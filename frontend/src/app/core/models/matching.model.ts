import { PromptKind } from './common.model';

export interface MatchingKeyword {
  keyword: string;
  frequency: number;
  covered: boolean;
}

export interface MatchingResult {
  score: number;
  keywords: MatchingKeyword[];
  missing: string[];
}

export interface CopilotPrompt {
  prompt: string;
  missing_keywords: string[];
}

/** Corps des appels matching / copilote : texte à comparer (absent > profil maître). */
export interface MatchRequest {
  text?: string | null;
}

export interface CopilotPromptRequest {
  text?: string | null;
  kind?: PromptKind;
}
