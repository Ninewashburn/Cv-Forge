import { HttpErrorResponse, HttpInterceptorFn, HttpResponse } from '@angular/common/http';
import { ErrorHandler, inject, Injectable, signal } from '@angular/core';
import { catchError, tap, throwError } from 'rxjs';

import { describeError, OFFLINE_MESSAGE, UNEXPECTED_MESSAGE, unwrapError } from './api/errors';

/**
 * Santé globale de l'application - le filet sous tous les autres.
 * `offline` : le serveur local ne répond plus (aucun appel n'aboutit).
 * `unexpected` : une erreur que personne n'a interceptée (bug). Dans les deux
 * cas le shell affiche un bandeau : une erreur n'est jamais invisible.
 */
@Injectable({ providedIn: 'root' })
export class AppStatus {
  readonly offline = signal(false);
  readonly unexpected = signal<string | null>(null);
  readonly offlineMessage = OFFLINE_MESSAGE;

  dismissUnexpected(): void {
    this.unexpected.set(null);
  }
}

/** Passe l'app « hors ligne » dès qu'un appel n'obtient aucune réponse ; la
 *  première réponse suivante (même une erreur métier) la remet en ligne. */
export const healthInterceptor: HttpInterceptorFn = (req, next) => {
  const status = inject(AppStatus);
  return next(req).pipe(
    tap((event) => {
      if (event instanceof HttpResponse) status.offline.set(false);
    }),
    catchError((err: unknown) => {
      if (err instanceof HttpErrorResponse) status.offline.set(err.status === 0);
      return throwError(() => err);
    }),
  );
};

/** Erreurs non interceptées (bug, appel sans gestion d'erreur) : affichées dans
 *  le bandeau plutôt qu'enfouies dans la console. Conserve le journal standard
 *  d'Angular (super) pour le diagnostic. */
@Injectable()
export class VisibleErrorHandler extends ErrorHandler {
  private readonly status = inject(AppStatus);

  override handleError(error: unknown): void {
    super.handleError(error);
    const cause = unwrapError(error);
    // Serveur arrêté : le bandeau « hors ligne » est déjà affiché par l'intercepteur.
    if (cause instanceof HttpErrorResponse && cause.status === 0) return;
    this.status.unexpected.set(describeError(cause, UNEXPECTED_MESSAGE));
  }
}
