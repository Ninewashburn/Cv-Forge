import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';
import { beforeEach, describe, expect, it, vi } from 'vitest';

import { MIN_CHARS, WizardStore } from './wizard-store';

const LONG = 'x'.repeat(MIN_CHARS);

/** Les portes du parcours : ce qui est fermé doit l être pour une raison
 *  dite à l utilisateur, et l Avant/Après reste un passage obligé. */
describe('WizardStore', () => {
  let store: WizardStore;
  let ctrl: HttpTestingController;

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [provideHttpClient(), provideHttpClientTesting()],
    });
    vi.spyOn(window, 'scrollTo').mockImplementation(() => undefined);
    store = TestBed.inject(WizardStore);
    ctrl = TestBed.inject(HttpTestingController);
  });

  it('n autorise l analyse qu avec une offre ET un CV assez longs', () => {
    expect(store.canAnalyse()).toBe(false);
    store.offerText.set(LONG);
    expect(store.canAnalyse()).toBe(false);
    store.cvText.set(LONG);
    expect(store.canAnalyse()).toBe(true);
  });

  it('explique pourquoi chaque étape est fermée', () => {
    expect(store.lockedReason(1)).toBeNull();
    expect(store.lockedReason(2)).toMatch(/étape 1/);
    expect(store.lockedReason(3)).toMatch(/étape 1/);
    expect(store.lockedReason(4)).toMatch(/étape 3/);
    expect(store.lockedReason(5)).toMatch(/étape 4/);
  });

  it('refuse de sauter une étape fermée', () => {
    store.goTo(3);
    expect(store.step()).toBe(1);
  });

  it('pré-remplit le CV adapté avec l original en entrant dans l adaptation', () => {
    store.cvText.set('Mon CV');
    store.analysis.set({ scoreCv: 50, scorePotential: null, hasLinkedin: false, keywords: [] });
    store.goTo(3);
    expect(store.step()).toBe(3);
    expect(store.adaptedText()).toBe('Mon CV');
    expect(store.lockedReason(4)).toBeNull();
  });

  it('réinitialise le diff validé quand le couple (original, adapté) change', () => {
    store.cvText.set('a');
    store.adaptedText.set('b');
    store.syncDiffSignature();
    store.toggleConfirmation(0);
    expect(store.confirmedAdditions().has(0)).toBe(true);

    store.syncDiffSignature(); // même couple : les confirmations tiennent
    expect(store.confirmedAdditions().has(0)).toBe(true);

    store.adaptedText.set('c');
    store.syncDiffSignature(); // couple différent : tout retombe
    expect(store.confirmedAdditions().size).toBe(0);
  });

  it('repart d une page blanche', () => {
    store.offerText.set(LONG);
    store.cvText.set(LONG);
    store.analysis.set({ scoreCv: 50, scorePotential: null, hasLinkedin: false, keywords: [] });
    store.goTo(3);
    store.reset();
    expect(store.step()).toBe(1);
    expect(store.offerText()).toBe('');
    expect(store.analysis()).toBeNull();
    expect(store.adaptedText()).toBe('');
    expect(store.hasUnsavedWork()).toBe(false);
  });

  it('dit en clair quand l analyse échoue', () => {
    store.offerText.set(LONG);
    store.cvText.set(LONG);
    store.analyse();
    ctrl.expectOne('/api/offers').error(new ProgressEvent('error'), { status: 0 });
    expect(store.busy()).toBe(false);
    expect(store.error()).toMatch(/CVForge ne répond plus/);
    expect(store.step()).toBe(1);
  });
});
