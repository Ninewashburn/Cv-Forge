import { ChangeDetectionStrategy, Component, computed, effect, inject } from '@angular/core';

import { addedSegments, diffStats, lcsDiff, paneSegments, PaneSegment, tokensOf } from '../diff';
import { WizardStore } from '../wizard-store';

/**
 * Étape 4 — Avant / Après ⭐ (nom interne : Diff Viewer).
 * Chaque passage ajouté doit être confirmé « vrai et prouvable » avant l'export.
 * Rendu par interpolation uniquement : le texte collé ne peut pas injecter de HTML.
 */
@Component({
  selector: 'cvforge-avant-apres',
  templateUrl: './avant-apres.html',
  styleUrl: './avant-apres.css',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class AvantApresStep {
  protected readonly store = inject(WizardStore);

  protected readonly tooLong: boolean;
  protected readonly left: PaneSegment[];
  protected readonly right: PaneSegment[];
  protected readonly additions: string[];
  protected readonly stats: { added: number; removed: number };

  // Le diff est figé à l'entrée de l'étape : les textes ne changent pas ici.
  constructor() {
    this.store.syncDiffSignature();
    const ops = lcsDiff(tokensOf(this.store.cvText()), tokensOf(this.store.adaptedText()));
    this.tooLong = ops === null;
    this.left = ops ? paneSegments(ops, 'left') : [];
    this.right = ops ? paneSegments(ops, 'right') : [];
    this.additions = ops ? addedSegments(ops) : [];
    this.stats = ops ? diffStats(ops) : { added: 0, removed: 0 };

    // La porte d'export s'ouvre quand tout est confirmé — et seulement si le
    // diff a pu être vérifié (passage par l'Avant/Après obligatoire).
    effect(() => this.store.exportReady.set(!this.tooLong && this.allConfirmed()));
  }

  protected readonly confirmedCount = computed(() => this.store.confirmedAdditions().size);
  protected readonly allConfirmed = computed(
    () => this.confirmedCount() >= this.additions.length,
  );

  protected isConfirmed(index: number): boolean {
    return this.store.confirmedAdditions().has(index);
  }
}
