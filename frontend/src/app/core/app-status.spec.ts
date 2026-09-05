import {
  HttpClient,
  HttpErrorResponse,
  provideHttpClient,
  withInterceptors,
} from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { ErrorHandler } from '@angular/core';
import { TestBed } from '@angular/core/testing';
import { beforeEach, describe, expect, it, vi } from 'vitest';

import { OFFLINE_MESSAGE, UNEXPECTED_MESSAGE } from './api/errors';
import { AppStatus, healthInterceptor, VisibleErrorHandler } from './app-status';

/** Le filet sous tous les autres : une erreur ne reste jamais invisible. */
describe('healthInterceptor', () => {
  let http: HttpClient;
  let ctrl: HttpTestingController;
  let status: AppStatus;

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [
        provideHttpClient(withInterceptors([healthInterceptor])),
        provideHttpClientTesting(),
      ],
    });
    http = TestBed.inject(HttpClient);
    ctrl = TestBed.inject(HttpTestingController);
    status = TestBed.inject(AppStatus);
  });

  it('passe hors ligne quand un appel n obtient aucune réponse', () => {
    http.get('/api/profile').subscribe({ error: () => undefined });
    ctrl.expectOne('/api/profile').error(new ProgressEvent('error'), { status: 0 });
    expect(status.offline()).toBe(true);
    expect(status.offlineMessage).toBe(OFFLINE_MESSAGE);
  });

  it('revient en ligne à la première réponse suivante, même une erreur métier', () => {
    http.get('/api/a').subscribe({ error: () => undefined });
    ctrl.expectOne('/api/a').error(new ProgressEvent('error'), { status: 0 });
    expect(status.offline()).toBe(true);

    http.get('/api/b').subscribe({ error: () => undefined });
    ctrl.expectOne('/api/b').flush({ detail: 'Fichier vide.' }, { status: 400, statusText: 'Bad' });
    expect(status.offline()).toBe(false);
  });

  it('laisse l erreur remonter à l écran appelant', () => {
    let caught: unknown;
    http.get('/api/c').subscribe({ error: (err: unknown) => (caught = err) });
    ctrl.expectOne('/api/c').flush({ detail: 'Nope' }, { status: 404, statusText: 'Not Found' });
    expect(caught).toBeInstanceOf(HttpErrorResponse);
  });
});

describe('VisibleErrorHandler', () => {
  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [{ provide: ErrorHandler, useClass: VisibleErrorHandler }],
    });
    vi.spyOn(console, 'error').mockImplementation(() => undefined);
  });

  it('affiche un message générique pour un bug non prévu', () => {
    TestBed.inject(ErrorHandler).handleError(new Error('bug'));
    expect(TestBed.inject(AppStatus).unexpected()).toBe(UNEXPECTED_MESSAGE);
  });

  it('reprend la phrase du backend pour une erreur HTTP non gérée', () => {
    const err = new HttpErrorResponse({ status: 400, error: { detail: 'Titre trop court.' } });
    TestBed.inject(ErrorHandler).handleError(err);
    expect(TestBed.inject(AppStatus).unexpected()).toBe('Titre trop court.');
  });

  it('ne double pas le bandeau hors ligne', () => {
    const status = TestBed.inject(AppStatus);
    TestBed.inject(ErrorHandler).handleError(new HttpErrorResponse({ status: 0 }));
    expect(status.unexpected()).toBeNull();
  });

  it('se ferme d un clic', () => {
    const status = TestBed.inject(AppStatus);
    TestBed.inject(ErrorHandler).handleError(new Error('bug'));
    status.dismissUnexpected();
    expect(status.unexpected()).toBeNull();
  });
});
