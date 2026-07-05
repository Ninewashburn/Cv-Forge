import { ChangeDetectionStrategy, Component, inject } from '@angular/core';

import { WizardStore } from '../wizard-store';

/** Étape 1 : les deux matières premières (offre + CV) + profil LinkedIn optionnel. */
@Component({
  selector: 'cvforge-sources',
  templateUrl: './sources.html',
  styleUrl: './sources.css',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class SourcesStep {
  protected readonly store = inject(WizardStore);
}
