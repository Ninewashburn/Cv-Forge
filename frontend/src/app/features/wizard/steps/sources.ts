import {
  ChangeDetectionStrategy,
  Component,
  DestroyRef,
  inject,
  signal,
  WritableSignal,
} from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';

import { ExtractService } from '../../../core/api';
import { WizardStore } from '../wizard-store';

type ImportTarget = 'offer' | 'cv' | 'linkedin';

/** Étape 1 : les deux matières premières (offre + CV) + profil LinkedIn optionnel. */
@Component({
  selector: 'cvforge-sources',
  templateUrl: './sources.html',
  styleUrl: './sources.css',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class SourcesStep {
  protected readonly store = inject(WizardStore);
  private readonly extractService = inject(ExtractService);
  private readonly destroyRef = inject(DestroyRef);

  /** Zone en cours de lecture de fichier (null = aucune). */
  protected readonly importing = signal<ImportTarget | null>(null);
  protected readonly importError = signal('');

  /** « Importer un fichier » : extraction locale, le texte reste éditable avant analyse. */
  protected onImportFile(target: ImportTarget, input: HTMLInputElement): void {
    const file = input.files?.[0];
    input.value = ''; // permet de resélectionner le même fichier
    if (!file || this.importing()) return;
    this.importing.set(target);
    this.importError.set('');
    this.extractService
      .extract(file)
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: ({ text }) => {
          this.importing.set(null);
          this.fieldOf(target).set(text);
        },
        error: (err: { error?: { detail?: string } }) => {
          this.importing.set(null);
          this.importError.set(
            err.error?.detail ??
              'Lecture du fichier impossible. Le copier-coller reste toujours possible.',
          );
        },
      });
  }

  private fieldOf(target: ImportTarget): WritableSignal<string> {
    switch (target) {
      case 'offer':
        return this.store.offerText;
      case 'cv':
        return this.store.cvText;
      case 'linkedin':
        return this.store.linkedinText;
    }
  }
}
