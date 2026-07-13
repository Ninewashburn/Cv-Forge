import { DatePipe } from '@angular/common';
import { ChangeDetectionStrategy, Component, inject } from '@angular/core';

import { ApplicationStatus } from '../../../core/models';
import { WizardStore } from '../wizard-store';

/** Étape 5 : export PDF + micro-suivi (réponse ? entretien ? - 3 clics max). */
@Component({
  selector: 'cvforge-export',
  imports: [DatePipe],
  templateUrl: './export.html',
  styleUrl: './export.css',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ExportStep {
  protected readonly store = inject(WizardStore);

  protected readonly statuses: readonly { value: ApplicationStatus; label: string }[] = [
    { value: 'envoyee', label: 'Envoyée' },
    { value: 'reponse', label: 'Réponse reçue' },
    { value: 'entretien', label: 'Entretien obtenu' },
    { value: 'refus', label: 'Refus' },
  ];

  protected onStatusChange(value: string): void {
    this.store.setApplicationStatus(value as ApplicationStatus);
  }
}
