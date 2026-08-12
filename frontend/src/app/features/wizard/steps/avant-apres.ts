import {
  ChangeDetectionStrategy,
  Component,
  computed,
  DestroyRef,
  effect,
  inject,
  signal,
} from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';

import { ProofService } from '../../../core/api';
import { addedSegments, diffStats, lcsDiff, paneSegments, PaneSegment, tokensOf } from '../diff';
import { WizardStore } from '../wizard-store';

/**
 * Étape 4 - Avant / Après ⭐ (nom interne : Diff Viewer).
 * Chaque passage ajouté doit être confirmé « vrai et prouvable » avant l'export.
 * Rendu par interpolation uniquement : le texte collé ne peut pas injecter de HTML.
 *
 * Boucle vertueuse (V1.5) : à côté de chaque confirmation, un champ optionnel
 * « Comment ? ». Rempli, il devient une preuve (note) dans la banque au clic
 * « Confirmé » - jamais forcé, et jamais bloquant pour la porte d'export.
 */
@Component({
  selector: 'cvforge-avant-apres',
  templateUrl: './avant-apres.html',
  styleUrl: './avant-apres.css',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class AvantApresStep {
  protected readonly store = inject(WizardStore);
  private readonly proofs = inject(ProofService);
  private readonly destroyRef = inject(DestroyRef);

  protected readonly tooLong: boolean;
  protected readonly left: PaneSegment[];
  protected readonly right: PaneSegment[];
  protected readonly additions: string[];
  protected readonly stats: { added: number; removed: number };

  // Preuve saisie par ajout : texte du champ « Comment ? », puis statut d'envoi.
  private readonly comments = signal<ReadonlyMap<number, string>>(new Map());
  private readonly savingProofs = signal<ReadonlySet<number>>(new Set());
  private readonly savedProofs = signal<ReadonlySet<number>>(new Set());
  private readonly failedProofs = signal<ReadonlySet<number>>(new Set());

  // Le diff est figé à l'entrée de l'étape : les textes ne changent pas ici.
  constructor() {
    this.store.syncDiffSignature();
    const ops = lcsDiff(tokensOf(this.store.cvText()), tokensOf(this.store.adaptedText()));
    this.tooLong = ops === null;
    this.left = ops ? paneSegments(ops, 'left') : [];
    this.right = ops ? paneSegments(ops, 'right') : [];
    this.additions = ops ? addedSegments(ops) : [];
    this.stats = ops ? diffStats(ops) : { added: 0, removed: 0 };

    // La porte d'export s'ouvre quand tout est confirmé - et seulement si le
    // diff a pu être vérifié (passage par l'Avant/Après obligatoire).
    effect(() => this.store.exportReady.set(!this.tooLong && this.allConfirmed()));
  }

  protected readonly confirmedCount = computed(() => this.store.confirmedAdditions().size);
  protected readonly allConfirmed = computed(() => this.confirmedCount() >= this.additions.length);

  protected isConfirmed(index: number): boolean {
    return this.store.confirmedAdditions().has(index);
  }

  protected commentOf(index: number): string {
    return this.comments().get(index) ?? '';
  }

  protected isSaving(index: number): boolean {
    return this.savingProofs().has(index);
  }

  protected isSaved(index: number): boolean {
    return this.savedProofs().has(index);
  }

  protected hasFailed(index: number): boolean {
    return this.failedProofs().has(index);
  }

  protected setComment(index: number, event: Event): void {
    const value = (event.target as HTMLTextAreaElement).value;
    const next = new Map(this.comments());
    next.set(index, value);
    this.comments.set(next);
  }

  /** Clic sur « Confirmer » : bascule la porte d'export, et si un « Comment ? »
   *  est saisi, en fait une preuve - uniquement à la bascule vers CONFIRMÉ. */
  protected confirm(index: number, claim: string): void {
    const wasConfirmed = this.isConfirmed(index);
    this.store.toggleConfirmation(index);
    if (wasConfirmed) return; // on vient de retirer la confirmation : rien à faire

    const comment = this.commentOf(index).trim();
    if (comment && !this.isSaved(index) && !this.isSaving(index)) {
      this.saveProof(index, claim, comment);
    }
  }

  /** Crée une preuve (note) dans la banque. Ne bloque JAMAIS la confirmation :
   *  un backend absent laisse l'ajout confirmé, avec un simple avertissement. */
  private saveProof(index: number, claim: string, comment: string): void {
    this.savingProofs.set(withIndex(this.savingProofs(), index));
    this.failedProofs.set(withoutIndex(this.failedProofs(), index));

    this.proofs
      .create({ type: 'note', title: proofTitle(claim), content: comment })
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: () => {
          this.savingProofs.set(withoutIndex(this.savingProofs(), index));
          this.savedProofs.set(withIndex(this.savedProofs(), index));
        },
        error: () => {
          this.savingProofs.set(withoutIndex(this.savingProofs(), index));
          this.failedProofs.set(withIndex(this.failedProofs(), index));
        },
      });
  }
}

/** Titre concis pour la preuve : le passage ajouté (le fait à prouver), borné. */
function proofTitle(claim: string): string {
  const clean = claim.replace(/\s+/g, ' ').trim();
  if (!clean) return 'Ajout confirme au CV';
  return clean.length > 120 ? `${clean.slice(0, 117)}...` : clean;
}

function withIndex(set: ReadonlySet<number>, index: number): ReadonlySet<number> {
  const next = new Set(set);
  next.add(index);
  return next;
}

function withoutIndex(set: ReadonlySet<number>, index: number): ReadonlySet<number> {
  const next = new Set(set);
  next.delete(index);
  return next;
}
