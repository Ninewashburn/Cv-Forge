import {
  ChangeDetectionStrategy,
  Component,
  computed,
  DestroyRef,
  inject,
  signal,
  WritableSignal,
} from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';

import { ExtractService } from '../../../core/api';
import { describeError } from '../../../core/api/errors';
import { WizardStore } from '../wizard-store';

type ImportTarget = 'offer' | 'cv' | 'linkedin';

const IMPORT_FALLBACK =
  "Ce fichier n'a pas pu être lu. Tu peux toujours copier son texte et le coller ici.";

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

  /** Ce qu'il manque encore pour lancer l'analyse - dit en clair, à côté du
   *  bouton, au lieu d'un bouton grisé sans explication. */
  protected readonly readiness = computed(() => {
    const offer = this.store.offerReady();
    const cv = this.store.cvReady();
    if (offer && cv) return 'Tout est prêt : lance la comparaison.';
    if (!offer && !cv) return "Pour commencer : colle l'offre d'emploi et ton CV ci-dessus.";
    if (!offer) return "Il manque l'offre d'emploi (ou son texte est trop court).";
    return 'Il manque ton CV (ou son texte est trop court).';
  });

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
        error: (err: unknown) => {
          this.importing.set(null);
          this.importError.set(describeError(err, IMPORT_FALLBACK));
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
