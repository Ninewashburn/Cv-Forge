import { ChangeDetectionStrategy, Component, inject } from '@angular/core';

import { AdaptationStep } from './steps/adaptation';
import { AnalyseStep } from './steps/analyse';
import { AvantApresStep } from './steps/avant-apres';
import { SourcesStep } from './steps/sources';
import { WizardStore } from './wizard-store';

/**
 * Atelier (parcours guidé). Blocs 1-2 de la Phase 4 : Sources, Analyse,
 * Adaptation et Avant/Après fonctionnels. L'Export (Bloc 3) reste à venir.
 */
@Component({
  selector: 'cvforge-wizard',
  imports: [SourcesStep, AnalyseStep, AdaptationStep, AvantApresStep],
  providers: [WizardStore],
  templateUrl: './wizard.html',
  styleUrl: './wizard.css',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class Wizard {
  protected readonly store = inject(WizardStore);

  protected readonly steps = [
    { n: 1, label: 'Sources' },
    { n: 2, label: 'Analyse' },
    { n: 3, label: 'Adaptation' },
    { n: 4, label: 'Avant / Après' },
    { n: 5, label: 'Export' },
  ] as const;

  protected disabled(n: number): boolean {
    if (n === 2 || n === 3) return this.store.analysis() === null;
    if (n === 4) return this.store.adaptedText().trim() === '';
    return n === 5; // Export : Bloc 3
  }
}
