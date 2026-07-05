import { ChangeDetectionStrategy, Component, inject } from '@angular/core';

import { AnalyseStep } from './steps/analyse';
import { SourcesStep } from './steps/sources';
import { WizardStore } from './wizard-store';

/**
 * Atelier (parcours guidé). Bloc 1 de la Phase 4 : Sources + Analyse fonctionnels,
 * branchés sur l'API (matching sans IA). Les étapes 3-5 arrivent dans les blocs suivants.
 */
@Component({
  selector: 'cvforge-wizard',
  imports: [SourcesStep, AnalyseStep],
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
    if (n === 2) return this.store.analysis() === null;
    return n > 2; // blocs suivants de la Phase 4
  }
}
