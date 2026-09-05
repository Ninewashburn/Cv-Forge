/**
 * Diff mot à mot (LCS), porté de CVForge Lite - fonctions pures, zéro DOM.
 *
 * Deux niveaux : d'abord les LIGNES (rapide, borne la taille du problème),
 * puis les MOTS à l'intérieur de chaque bloc modifié. Un CV de n'importe
 * quelle longueur passe : au pire, un bloc trop gros est marqué en entier
 * (lignes retirées / ajoutées) au lieu de mot à mot - jamais d'impasse.
 *
 * Sécurité : la sortie est une liste de segments TYPÉS rendus par interpolation
 * Angular (`{{ }}`), jamais par `innerHTML`. L'échappement du texte collé par
 * l'utilisateur est donc garanti par le framework (cf. ROADMAP - audit V1.5).
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

/** Diff LCS générique ; `null` si le tableau dépasse le garde-fou mémoire.
 *  Le début et la fin communs sont retirés AVANT le tableau : une retouche
 *  isolée dans un long texte ne coûte que la taille de la retouche. */
export function lcsDiff(a: string[], b: string[]): DiffOp[] | null {
  let prefix = 0;
  while (prefix < a.length && prefix < b.length && a[prefix] === b[prefix]) prefix++;
  let suffix = 0;
  while (
    suffix < a.length - prefix &&
    suffix < b.length - prefix &&
    a[a.length - 1 - suffix] === b[b.length - 1 - suffix]
  ) {
    suffix++;
  }
  const middle = lcsCore(a.slice(prefix, a.length - suffix), b.slice(prefix, b.length - suffix));
  if (middle === null) return null;
  return [
    ...asOps(a.slice(0, prefix), 'same'),
    ...middle,
    ...asOps(a.slice(a.length - suffix), 'same'),
  ];
}

function lcsCore(a: string[], b: string[]): DiffOp[] | null {
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

function linesOf(text: string): string[] {
  return text.replace(/\r\n?/g, NEWLINE).split(NEWLINE);
}

/** Tokens d'une suite de lignes, chaque ligne suivie de son saut. */
function lineTokens(lines: string[]): string[] {
  return lines.flatMap((line) => [...tokensOf(line), NEWLINE]);
}

const asOps = (tokens: string[], kind: DiffKind): DiffOp[] =>
  tokens.map((token) => ({ kind, token }));

/** Bloc modifié : mot à mot si le budget le permet, sinon lignes entières. */
function hunkOps(removedLines: string[], addedLines: string[]): DiffOp[] {
  const a = lineTokens(removedLines);
  const b = lineTokens(addedLines);
  return lcsDiff(a, b) ?? [...asOps(a, 'removed'), ...asOps(b, 'added')];
}

/**
 * Diff complet de deux textes. Ne renvoie JAMAIS `null` : les lignes
 * identiques sont alignées d'abord (peu coûteux), et seuls les blocs modifiés
 * passent au mot à mot. Résultat équivalent au diff global sur un CV
 * ordinaire, et une sortie toujours exploitable sur un texte démesuré.
 */
export function diffText(before: string, after: string): DiffOp[] {
  const beforeLines = linesOf(before);
  const afterLines = linesOf(after);
  const lineOps = lcsDiff(beforeLines, afterLines) ?? [
    ...asOps(beforeLines, 'removed'),
    ...asOps(afterLines, 'added'),
  ];

  const ops: DiffOp[] = [];
  let removed: string[] = [];
  let added: string[] = [];
  const flush = (): void => {
    if (removed.length > 0 || added.length > 0) ops.push(...hunkOps(removed, added));
    removed = [];
    added = [];
  };
  for (const op of lineOps) {
    if (op.kind === 'same') {
      flush();
      ops.push(...asOps(tokensOf(op.token), 'same'), { kind: 'same', token: NEWLINE });
    } else if (op.kind === 'removed') {
      removed.push(op.token);
    } else {
      added.push(op.token);
    }
  }
  flush();
  // Chaque ligne a reçu un saut : le dernier est artificiel, on le retire.
  while (ops.length > 0 && ops[ops.length - 1].token === NEWLINE) ops.pop();
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

/** Passages ajoutés consécutifs - à confirmer « vrai et prouvable » un par un. */
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
