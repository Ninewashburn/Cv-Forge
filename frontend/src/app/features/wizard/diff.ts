/**
 * Diff mot à mot (LCS), porté de CVForge Lite — fonctions pures, zéro DOM.
 *
 * Sécurité : la sortie est une liste de segments TYPÉS rendus par interpolation
 * Angular (`{{ }}`), jamais par `innerHTML`. L'échappement du texte collé par
 * l'utilisateur est donc garanti par le framework (cf. ROADMAP — audit V1.5).
 */

export type DiffKind = 'same' | 'removed' | 'added';

export interface DiffOp {
  readonly kind: DiffKind;
  readonly token: string;
}

/** Segment prêt à afficher dans un volet (mots adjacents de même type fusionnés). */
export type PaneSegment =
  | { readonly type: 'text'; readonly kind: DiffKind; readonly text: string }
  | { readonly type: 'break' };

const NEWLINE = '\n';
/** Garde-fou mémoire du DP (même seuil que Lite). */
const MAX_CELLS = 4_000_000;

export function tokensOf(text: string): string[] {
  return text
    .replace(/\r\n?/g, NEWLINE)
    .split(/(\n)|[ \t]+/)
    .filter((t): t is string => t !== undefined && t !== '');
}

/** Diff LCS ; `null` si les textes sont trop longs pour le DP. */
export function lcsDiff(a: string[], b: string[]): DiffOp[] | null {
  const n = a.length;
  const m = b.length;
  if (n * m > MAX_CELLS) return null;

  const dp: Int32Array[] = Array.from({ length: n + 1 }, () => new Int32Array(m + 1));
  for (let i = n - 1; i >= 0; i--) {
    for (let j = m - 1; j >= 0; j--) {
      dp[i][j] = a[i] === b[j] ? dp[i + 1][j + 1] + 1 : Math.max(dp[i + 1][j], dp[i][j + 1]);
    }
  }

  const ops: DiffOp[] = [];
  let i = 0;
  let j = 0;
  while (i < n && j < m) {
    if (a[i] === b[j]) {
      ops.push({ kind: 'same', token: a[i] });
      i++;
      j++;
    } else if (dp[i + 1][j] >= dp[i][j + 1]) {
      ops.push({ kind: 'removed', token: a[i] });
      i++;
    } else {
      ops.push({ kind: 'added', token: b[j] });
      j++;
    }
  }
  while (i < n) ops.push({ kind: 'removed', token: a[i++] });
  while (j < m) ops.push({ kind: 'added', token: b[j++] });
  return ops;
}

/** Volet « avant » (side=left : same + removed) ou « après » (side=right : same + added). */
export function paneSegments(ops: DiffOp[], side: 'left' | 'right'): PaneSegment[] {
  const skip: DiffKind = side === 'left' ? 'added' : 'removed';
  const segments: PaneSegment[] = [];
  let currentKind: DiffKind | null = null;
  let words: string[] = [];

  const flush = (): void => {
    if (currentKind !== null && words.length > 0) {
      segments.push({ type: 'text', kind: currentKind, text: words.join(' ') });
    }
    words = [];
    currentKind = null;
  };

  for (const op of ops) {
    if (op.token === NEWLINE) {
      if (op.kind !== skip) {
        flush();
        segments.push({ type: 'break' });
      }
      continue;
    }
    if (op.kind === skip) continue;
    if (op.kind !== currentKind) flush();
    currentKind = op.kind;
    words.push(op.token);
  }
  flush();
  return segments;
}

/** Passages ajoutés consécutifs — à confirmer « vrai et prouvable » un par un. */
export function addedSegments(ops: DiffOp[]): string[] {
  const segments: string[] = [];
  let current: string[] = [];
  for (const op of ops) {
    if (op.kind === 'added' && op.token !== NEWLINE) {
      current.push(op.token);
    } else if (current.length > 0) {
      segments.push(current.join(' '));
      current = [];
    }
  }
  if (current.length > 0) segments.push(current.join(' '));
  return segments;
}

export function diffStats(ops: DiffOp[]): { added: number; removed: number } {
  let added = 0;
  let removed = 0;
  for (const op of ops) {
    if (op.token === NEWLINE) continue;
    if (op.kind === 'added') added++;
    else if (op.kind === 'removed') removed++;
  }
  return { added, removed };
}
