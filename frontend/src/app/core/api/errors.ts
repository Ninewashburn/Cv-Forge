import { HttpErrorResponse } from '@angular/common/http';

/** CVForge tourne en local : si un appel n'obtient AUCUNE réponse, c'est que
 *  l'application elle-même est arrêtée - pas « le réseau ». */
export const OFFLINE_MESSAGE =
  "CVForge ne répond plus. Ferme l'application, puis relance-la - ton travail enregistré est conservé.";

/** Bug non prévu, côté interface : on le dit, sans jargon, et on rassure sur les données. */
export const UNEXPECTED_MESSAGE =
  "Une erreur inattendue s'est produite. Ton travail enregistré est conservé : réessaie, ou ferme puis relance l'application.";

/**
 * Message lisible par tout le monde à partir d'une erreur d'appel API.
 * - Aucune réponse (status 0) : l'application locale est arrêtée.
 * - `detail` texte : c'est la phrase rédigée par le backend, déjà en français.
 * - Sinon : le message de repli fourni par l'écran appelant.
 * Jamais de code HTTP ni de trace technique à l'écran.
 */
export function describeError(err: unknown, fallback: string): string {
  const cause = unwrapError(err);
  if (cause instanceof HttpErrorResponse) {
    if (cause.status === 0) return OFFLINE_MESSAGE;
    const detail: unknown = cause.error?.detail;
    if (typeof detail === 'string' && detail.trim()) return detail;
  }
  return fallback;
}

/** Angular enveloppe parfois l'erreur d'une promesse rejetée dans `{ rejection }`. */
export function unwrapError(err: unknown): unknown {
  if (err && typeof err === 'object' && 'rejection' in err) {
    return (err as { rejection: unknown }).rejection;
  }
  return err;
}
