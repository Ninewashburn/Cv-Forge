/** Niveau clé API (adaptation contrôlée, niveau 2) - la clé ne transite jamais vers l'UI. */

export interface LlmConfig {
  provider: string;
  model: string;
  configured: boolean;
  /** Indice type « ...abcd » - jamais la clé complète. */
  key_hint: string | null;
}

/** Proposition du fournisseur - à valider dans l'Avant/Après, jamais auto-appliquée. */
export interface AdaptResult {
  adapted_text: string;
  provider: string;
  model: string;
}
