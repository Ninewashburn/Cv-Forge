import { ChangeDetectionStrategy, Component, DestroyRef, inject, signal } from '@angular/core';
import { takeUntilDestroyed, toObservable } from '@angular/core/rxjs-interop';
import { debounceTime, distinctUntilChanged, of, switchMap } from 'rxjs';

import { MatchingResult, PromptKind } from '../../../core/models';
import { WizardStore } from '../wizard-store';

interface PromptIntent {
  readonly kind: PromptKind;
  readonly label: string;
  readonly hint: string;
}

/** Étape 3 : adaptation contrôlée — édition manuelle + mode copilote (4 intentions). */
@Component({
  selector: 'cvforge-adaptation',
  templateUrl: './adaptation.html',
  styleUrl: './adaptation.css',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class AdaptationStep {
  protected readonly store = inject(WizardStore);
  private readonly destroyRef = inject(DestroyRef);

  protected readonly live = signal<MatchingResult | null>(null);
  protected readonly promptText = signal('');
  protected readonly promptBusy = signal(false);
  protected readonly copyHint = signal('');
  protected readonly kind = signal<PromptKind>('adapter');

  protected readonly intents: readonly PromptIntent[] = [
    { kind: 'adapter', label: 'Adapter', hint: "Reformuler le CV pour l'offre (défaut)" },
    { kind: 'auditer', label: 'Auditer', hint: 'Critique de recruteur — ne réécrit rien' },
    { kind: 'muscler', label: 'Muscler', hint: "Verbes d'action, sans inventer de chiffres" },
    { kind: 'accrocher', label: 'Accrocher', hint: 'Accroche 3 lignes, que du vérifiable' },
  ];

  constructor() {
    // Matching en direct : recalcul (sans IA) à chaque pause de frappe.
    toObservable(this.store.adaptedText)
      .pipe(
        debounceTime(350),
        distinctUntilChanged(),
        switchMap((text) => (text.trim() ? this.store.liveMatch(text) : of(null))),
        takeUntilDestroyed(),
      )
      .subscribe((result) => this.live.set(result));
  }

  protected preparePrompt(): void {
    if (this.promptBusy()) return;
    this.promptBusy.set(true);
    this.copyHint.set('');
    this.store
      .buildPrompt(this.kind())
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: (result) => {
          this.promptText.set(result.prompt);
          this.promptBusy.set(false);
        },
        error: () => {
          this.copyHint.set('Erreur — backend indisponible ?');
          this.promptBusy.set(false);
        },
      });
  }

  protected async copyPrompt(): Promise<void> {
    try {
      await navigator.clipboard.writeText(this.promptText());
      this.copyHint.set('Copié — colle-le dans ton IA.');
    } catch {
      this.copyHint.set('Copie impossible — sélectionne le texte à la main.');
    }
  }

  protected resetAdapted(): void {
    this.store.adaptedText.set(this.store.cvText());
  }
}
