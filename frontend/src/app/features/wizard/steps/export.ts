import { DatePipe } from '@angular/common';
import { ChangeDetectionStrategy, Component, DestroyRef, inject } from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';

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
  private readonly destroyRef = inject(DestroyRef);

  protected readonly statuses: readonly { value: ApplicationStatus; label: string }[] = [
    { value: 'envoyee', label: 'Envoyée' },
    { value: 'reponse', label: 'Réponse reçue' },
    { value: 'entretien', label: 'Entretien obtenu' },
    { value: 'refus', label: 'Refus' },
  ];

  /** Changement de statut : la valeur est validée contre la liste (pas de cast),
   *  et en cas d'échec le sélecteur revient à la valeur précédente. */
  protected onStatusChange(select: HTMLSelectElement): void {
    const previous = this.store.application()?.status;
    const next = this.statuses.find((s) => s.value === select.value)?.value;
    if (!next || next === previous) return;
    this.store
      .setApplicationStatus(next)
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        error: () => {
          if (previous) select.value = previous; // le message d'erreur est dans le store
        },
      });
  }
}
