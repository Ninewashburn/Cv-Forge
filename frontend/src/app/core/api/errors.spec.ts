import { HttpErrorResponse } from '@angular/common/http';
import { describe, expect, it } from 'vitest';

import { describeError, OFFLINE_MESSAGE, unwrapError } from './errors';

/** Tout message d'erreur affiché passe par ici : il doit être en français
 *  simple, jamais un code HTTP, jamais « [object Object] ». */
describe('describeError', () => {
  it('reconnaît le serveur local arrêté (aucune réponse)', () => {
    const err = new HttpErrorResponse({ status: 0, error: new ProgressEvent('error') });
    expect(describeError(err, 'repli')).toBe(OFFLINE_MESSAGE);
  });

  it('reprend la phrase du backend quand elle existe', () => {
    const err = new HttpErrorResponse({ status: 400, error: { detail: 'Ce PDF est illisible.' } });
    expect(describeError(err, 'repli')).toBe('Ce PDF est illisible.');
  });

  it('retombe sur le message de repli si le détail n est pas une phrase', () => {
    const list = new HttpErrorResponse({ status: 422, error: { detail: [{ msg: 'x' }] } });
    expect(describeError(list, 'repli')).toBe('repli');
    const empty = new HttpErrorResponse({ status: 500, error: { detail: '   ' } });
    expect(describeError(empty, 'repli')).toBe('repli');
    const html = new HttpErrorResponse({ status: 502, error: '<html>Bad Gateway</html>' });
    expect(describeError(html, 'repli')).toBe('repli');
  });

  it('retombe sur le repli pour une erreur qui n est pas HTTP', () => {
    expect(describeError(new Error('boom'), 'repli')).toBe('repli');
    expect(describeError(undefined, 'repli')).toBe('repli');
  });

  it('déballe une promesse rejetée enveloppée par Angular', () => {
    const inner = new HttpErrorResponse({ status: 0 });
    expect(unwrapError({ rejection: inner })).toBe(inner);
    expect(describeError({ rejection: inner }, 'repli')).toBe(OFFLINE_MESSAGE);
  });
});
