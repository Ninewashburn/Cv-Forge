import { ChangeDetectionStrategy, Component, inject } from '@angular/core';

import { AdaptationStep } from './steps/adaptation';
import { AnalyseStep } from './steps/analyse';
import { AvantApresStep } from './steps/avant-apres';
import { ExportStep } from './steps/export';
import { SourcesStep } from './steps/sources';
import { WizardStore } from './wizard-store';

/**
 * Atelier (parcours guidé) — le core loop V1 complet :
 * Sources → Analyse → Adaptation → Avant/Après → Export PDF + micro-suivi.
 */
@Component({
  selector: 'cvforge-wizard',
  imports: [SourcesStep, AnalyseStep, AdaptationStep, AvantApresStep, ExportStep],
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
    if (n === 5) return !this.store.exportReady();
    return false;
  }
}
