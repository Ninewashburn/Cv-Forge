import { afterEach, describe, expect, it, vi } from 'vitest';

import { downloadBlob, fileSlug } from './download';

describe('fileSlug', () => {
  it('retire accents et ponctuation, garde un nom lisible', () => {
    expect(fileSlug('Développeur Full-Stack (H/F) !', 'offre')).toBe('Developpeur-Full-Stack-H-F');
  });

  it('retombe sur le nom de repli quand il ne reste rien', () => {
    expect(fileSlug('', 'offre')).toBe('offre');
    expect(fileSlug('???', 'offre')).toBe('offre');
  });

  it('borne la longueur à 60 caractères', () => {
    expect(fileSlug('a'.repeat(200), 'offre')).toHaveLength(60);
  });
});

describe('downloadBlob', () => {
  afterEach(() => vi.restoreAllMocks());

  it('déclenche un lien de téléchargement portant le nom demandé', () => {
    // jsdom n'implémente pas les URL d'objet : on les simule.
    const create = vi.fn(() => 'blob:cvforge');
    const revoke = vi.fn();
    vi.stubGlobal('URL', { ...URL, createObjectURL: create, revokeObjectURL: revoke });
    const click = vi.spyOn(HTMLAnchorElement.prototype, 'click').mockImplementation(function (
      this: HTMLAnchorElement,
    ) {
      expect(this.download).toBe('cv-adapte.pdf');
      expect(this.href).toBe('blob:cvforge');
    });

    downloadBlob(new Blob(['%PDF']), 'cv-adapte.pdf');

    expect(create).toHaveBeenCalledTimes(1);
    expect(click).toHaveBeenCalledTimes(1);
    expect(revoke).toHaveBeenCalledWith('blob:cvforge');
    vi.unstubAllGlobals();
  });
});
