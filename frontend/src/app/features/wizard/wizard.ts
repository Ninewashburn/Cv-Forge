import { ChangeDetectionStrategy, Component, inject, signal } from '@angular/core';

import { AdaptationStep } from './steps/adaptation';
import { AnalyseStep } from './steps/analyse';
import { AvantApresStep } from './steps/avant-apres';
import { ExportStep } from './steps/export';
import { SourcesStep } from './steps/sources';
import { WizardStore } from './wizard-store';

/**
 * Atelier (parcours guidé) - le core loop V1 complet :
 * Sources > Analyse > Adaptation > Avant/Après > Export PDF + micro-suivi.
 */
@Component({
  selector: 'cvforge-wizard',
  imports: [SourcesStep, AnalyseStep, AdaptationStep, AvantApresStep, ExportStep],
  templateUrl: './wizard.html',
  styleUrl: './wizard.css',
  changeDetection: ChangeDetectionStrategy.OnPush,
  host: { '(window:beforeunload)': 'onBeforeUnload($event)' },
})
export class Wizard {
  protected readonly store = inject(WizardStore);

  /** Explication affichée quand on clique sur une étape encore fermée. */
  protected readonly lockNote = signal('');

  protected readonly steps = [
    { n: 1, label: 'Sources' },
    { n: 2, label: 'Analyse' },
    { n: 3, label: 'Adaptation' },
    { n: 4, label: 'Avant / Après' },
    { n: 5, label: 'Export' },
  ] as const;

  protected locked(n: number): boolean {
    return this.store.lockedReason(n) !== null;
  }

  /** Une étape fermée reste cliquable : le clic explique pourquoi elle l'est,
   *  au lieu d'un bouton grisé muet. */
  protected select(n: number): void {
    const reason = this.store.lockedReason(n);
    this.lockNote.set(reason ?? '');
    if (reason === null) this.store.goTo(n);
  }

  /** Filet à la fermeture de l'onglet : le parcours vit en mémoire tant que
   *  rien n'est exporté - le navigateur demande confirmation avant de fermer. */
  protected onBeforeUnload(event: BeforeUnloadEvent): void {
    if (this.store.hasUnsavedWork()) event.preventDefault();
  }

  protected restart(): void {
    if (!this.store.hasUnsavedWork() || window.confirm('Tout effacer et repartir de zéro ?')) {
      this.lockNote.set('');
      this.store.reset();
    }
  }
}
