import { describe, expect, it } from 'vitest';

import { addedSegments, diffStats, diffText, lcsDiff, paneSegments, tokensOf } from './diff';

/** Le Diff Viewer est l'organe qui garantit que rien ne s'exporte sans
 *  confirmation : un passage ajouté qui n'apparaîtrait pas dans
 *  `addedSegments` casserait la promesse sans que rien ne plante. */
describe('tokensOf', () => {
  it('découpe sur les espaces et garde les sauts de ligne comme tokens', () => {
    expect(tokensOf('a b\nc')).toEqual(['a', 'b', '\n', 'c']);
  });

  it('normalise les fins de ligne Windows et ignore les espaces multiples', () => {
    expect(tokensOf('a  \t b\r\nc')).toEqual(['a', 'b', '\n', 'c']);
  });
});

describe('lcsDiff', () => {
  it('marque ce qui est commun, retiré et ajouté', () => {
    const ops = lcsDiff(['a', 'b', 'c'], ['a', 'x', 'c']);
    expect(ops).toEqual([
      { kind: 'same', token: 'a' },
      { kind: 'removed', token: 'b' },
      { kind: 'added', token: 'x' },
      { kind: 'same', token: 'c' },
    ]);
  });

  it('renvoie null au-delà du garde-fou mémoire', () => {
    // Deux textes sans rien en commun : le tableau DP ferait 2100 x 2100.
    const a = Array.from({ length: 2100 }, (_, i) => `a${i}`);
    const b = Array.from({ length: 2100 }, (_, i) => `b${i}`);
    expect(lcsDiff(a, b)).toBeNull();
  });

  it('ignore le début et la fin communs avant de comparer', () => {
    // Même taille, mais une seule ligne diffère : pas de garde-fou, résultat exact.
    const a = Array.from({ length: 2100 }, (_, i) => `l${i}`);
    const b = [...a.slice(0, 1000), 'autre', ...a.slice(1001)];
    const ops = lcsDiff(a, b);
    expect(ops).not.toBeNull();
    expect(ops?.filter((op) => op.kind !== 'same')).toEqual([
      { kind: 'removed', token: 'l1000' },
      { kind: 'added', token: 'autre' },
    ]);
  });
});

describe('diffText', () => {
  it('ne signale rien quand les textes sont identiques', () => {
    const text = 'Lina Carvalho\n\nEXPERIENCE\n- Angular et TypeScript';
    const ops = diffText(text, text);
    expect(ops.every((op) => op.kind === 'same')).toBe(true);
    expect(diffStats(ops)).toEqual({ added: 0, removed: 0 });
    expect(addedSegments(ops)).toEqual([]);
  });

  it('repère un mot ajouté au milieu d une ligne', () => {
    const ops = diffText('API REST en Spring Boot', 'API REST sécurisée en Spring Boot');
    expect(addedSegments(ops)).toEqual(['sécurisée']);
    expect(diffStats(ops)).toEqual({ added: 1, removed: 0 });
  });

  it('sépare les ajouts par ligne, pour une confirmation par passage', () => {
    const ops = diffText('Titre\n- a', 'Titre\n- a\n- Docker en production\n- Kubernetes');
    expect(addedSegments(ops)).toEqual(['- Docker en production', '- Kubernetes']);
  });

  it('ne compte pas un simple reflow de paragraphe comme un ajout', () => {
    const before = 'Je développe des\napplications web';
    const after = 'Je développe des applications web';
    const ops = diffText(before, after);
    expect(addedSegments(ops)).toEqual([]);
    expect(diffStats(ops)).toEqual({ added: 0, removed: 0 });
  });

  it('restitue chaque volet avec ses propres mots', () => {
    const ops = diffText('un deux\ntrois', 'un 2\ntrois');
    expect(paneSegments(ops, 'left')).toEqual([
      { type: 'text', kind: 'same', text: 'un' },
      { type: 'text', kind: 'removed', text: 'deux' },
      { type: 'break' },
      { type: 'text', kind: 'same', text: 'trois' },
    ]);
    expect(paneSegments(ops, 'right')).toEqual([
      { type: 'text', kind: 'same', text: 'un' },
      { type: 'text', kind: 'added', text: '2' },
      { type: 'break' },
      { type: 'text', kind: 'same', text: 'trois' },
    ]);
  });

  it('gère les textes vides sans planter', () => {
    expect(diffText('', '')).toEqual([]);
    expect(addedSegments(diffText('', 'Nouveau'))).toEqual(['Nouveau']);
    expect(diffStats(diffText('Ancien', ''))).toEqual({ added: 0, removed: 1 });
  });

  it('ne renvoie jamais une impasse sur un texte démesuré', () => {
    // 3 000 lignes de chaque côté, toutes différentes : le mot à mot global
    // dépasserait le garde-fou. Ici le résultat reste exploitable (lignes
    // entières), et l export reste possible après confirmation.
    const before = Array.from({ length: 3000 }, (_, i) => `avant ${i}`).join('\n');
    const after = Array.from({ length: 3000 }, (_, i) => `apres ${i}`).join('\n');
    const ops = diffText(before, after);
    expect(ops.length).toBeGreaterThan(0);
    expect(diffStats(ops)).toEqual({ added: 6000, removed: 6000 });
  });

  it('reste rapide et précis sur un long CV avec une seule retouche', () => {
    const lines = Array.from({ length: 2500 }, (_, i) => `ligne ${i} du CV`);
    const before = lines.join('\n');
    const after = [
      ...lines.slice(0, 1200),
      'ligne 1200 du CV certifiée',
      ...lines.slice(1201),
    ].join('\n');
    const ops = diffText(before, after);
    expect(addedSegments(ops)).toEqual(['certifiée']);
    expect(diffStats(ops)).toEqual({ added: 1, removed: 0 });
  });
});
