import { ChangeDetectionStrategy, Component, DestroyRef, inject, signal } from '@angular/core';
import { takeUntilDestroyed, toObservable } from '@angular/core/rxjs-interop';
import { debounceTime, distinctUntilChanged, of, switchMap } from 'rxjs';

import { LlmService } from '../../../core/api';
import { LlmConfig, MatchingResult, PromptKind } from '../../../core/models';
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
  private readonly llm = inject(LlmService);
  private readonly destroyRef = inject(DestroyRef);

  protected readonly live = signal<MatchingResult | null>(null);
  protected readonly promptText = signal('');
  protected readonly promptBusy = signal(false);
  protected readonly copyHint = signal('');
  protected readonly kind = signal<PromptKind>('adapter');

  // --- Niveau clé API (niveau 2) -----------------------------------------
  protected readonly llmConfig = signal<LlmConfig | null>(null);
  protected readonly keyInput = signal('');
  protected readonly savingKey = signal(false);
  /** Consentement explicite : coché à chaque session, jamais présumé. */
  protected readonly consent = signal(false);
  protected readonly adapting = signal(false);
  protected readonly apiHint = signal('');

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

    this.reloadLlmConfig();
  }

  private reloadLlmConfig(): void {
    this.llm
      .getConfig()
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: (config) => this.llmConfig.set(config),
        error: () => this.llmConfig.set(null),
      });
  }

  protected saveKey(): void {
    const key = this.keyInput().trim();
    if (!key || this.savingKey()) return;
    this.savingKey.set(true);
    this.apiHint.set('');
    this.llm
      .saveConfig(key)
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: (config) => {
          this.savingKey.set(false);
          this.keyInput.set(''); // la clé ne reste jamais dans le navigateur
          this.llmConfig.set(config);
          this.apiHint.set('Clé enregistrée sur ta machine (jamais dans le navigateur).');
        },
        error: (err: { error?: { detail?: string } }) => {
          this.savingKey.set(false);
          this.apiHint.set(err.error?.detail ?? 'Enregistrement de la clé impossible.');
        },
      });
  }

  protected removeKey(): void {
    if (!window.confirm('Retirer ta clé API de cette machine ?')) return;
    this.llm
      .removeConfig()
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe(() => {
        this.consent.set(false);
        this.apiHint.set('');
        this.reloadLlmConfig();
      });
  }

  protected runAdapt(): void {
    if (this.adapting() || !this.consent() || !this.llmConfig()?.configured) return;
    this.adapting.set(true);
    this.apiHint.set('');
    this.store
      .adaptWithApi(this.kind())
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: (result) => {
          this.adapting.set(false);
          // Proposition, jamais appliquée en silence : elle remplace le champ
          // éditable, et l'export reste verrouillé tant que l'Avant/Après
          // n'a pas été validé (porte d'intégrité du store).
          this.store.adaptedText.set(result.adapted_text);
          this.apiHint.set(
            `Proposition de ${result.model} reçue — vérifie chaque changement dans l'Avant / Après.`,
          );
        },
        error: (err: { error?: { detail?: string } }) => {
          this.adapting.set(false);
          this.apiHint.set(err.error?.detail ?? 'Appel au fournisseur impossible.');
        },
      });
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
