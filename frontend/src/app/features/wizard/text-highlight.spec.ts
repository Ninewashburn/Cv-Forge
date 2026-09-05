import { describe, expect, it } from 'vitest';

import { buildHighlightSegments, normalizeToken, stem } from './text-highlight';

/** `stem` est le miroir TS de keyword_engine.py : les mêmes familles doivent
 *  se rejoindre ici, sinon le surlignage live ne suit plus le score. */
describe('stem (miroir du moteur Python)', () => {
  it.each([
    ['deploiement', 'deployer', 'deploye', 'deploiee'],
    ['developpement', 'developper', 'developpeur', 'developpeuse'],
    ['configuration', 'configurer', 'configure'],
    ['administrateur', 'administration', 'administrer', 'administratrice'],
    ['utilisateur', 'utilisation', 'utiliser'],
    ['analyse', 'analyser', 'analyses'],
    ['management', 'manager'],
    ['reseaux', 'reseau'],
  ])('réunit la famille %s', (...family) => {
    const stems = new Set(family.map(stem));
    expect(stems.size).toBe(1);
  });

  it.each([
    ['gestion', 'geste'],
    ['important', 'importer'],
    ['portable', 'port'],
    ['forme', 'formation'],
  ])('ne confond pas %s et %s', (left, right) => {
    expect(stem(left)).not.toBe(stem(right));
  });

  it('laisse les technos courtes intactes', () => {
    for (const tech of ['docker', 'angular', 'python', 'java', 'sql', 'c#', '.net']) {
      expect(stem(tech)).toBe(tech);
    }
  });
});

describe('normalizeToken', () => {
  it('retire les accents et les ligatures', () => {
    expect(normalizeToken('Développeur au Cœur')).toBe('developpeur au coeur');
  });
});

describe('buildHighlightSegments', () => {
  it('surligne les mots-clés couverts, y compris via une variante de la famille', () => {
    const segments = buildHighlightSegments('Déploiement continu avec Docker', [
      'deployer',
      'docker',
    ]);
    const keywords = segments.filter((s) => s.kind === 'keyword').map((s) => s.text);
    expect(keywords).toEqual(['Déploiement', 'Docker']);
  });

  it('repère les lignes de section et les laisse hors surlignage', () => {
    const segments = buildHighlightSegments('EXPÉRIENCE\nAngular', ['angular']);
    expect(segments[0]).toEqual({ text: 'EXPÉRIENCE', kind: 'section' });
    expect(segments.some((s) => s.kind === 'keyword' && s.text === 'Angular')).toBe(true);
  });

  it('restitue le texte intégralement, dans l ordre', () => {
    const text = 'Un texte, avec ponctuation !\nEt deux lignes.';
    const rebuilt = buildHighlightSegments(text, [])
      .map((s) => s.text)
      .join('');
    // Une ligne fantôme finale est ajoutée pour suivre le scroll du textarea.
    expect(rebuilt).toBe(text + '\n');
  });
});
