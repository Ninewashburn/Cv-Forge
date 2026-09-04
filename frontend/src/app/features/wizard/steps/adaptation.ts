import {
  ChangeDetectionStrategy,
  Component,
  computed,
  DestroyRef,
  inject,
  signal,
} from '@angular/core';
import { takeUntilDestroyed, toObservable } from '@angular/core/rxjs-interop';
import { catchError, debounceTime, distinctUntilChanged, EMPTY, of, switchMap } from 'rxjs';

import { LlmService } from '../../../core/api';
import { describeError } from '../../../core/api/errors';
import { fail, LlmConfig, MatchingResult, Notice, ok, PromptKind } from '../../../core/models';
import { buildHighlightSegments } from '../text-highlight';
import { WizardStore } from '../wizard-store';

interface PromptIntent {
  readonly kind: PromptKind;
  readonly label: string;
  readonly hint: string;
}

/** Étape 3 : adaptation contrôlée - édition manuelle + mode copilote (4 intentions). */
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
  /** Le dernier recalcul a échoué : le score affiché n'est plus à jour. Dit à l'écran. */
  protected readonly liveError = signal(false);
  protected readonly promptText = signal('');
  protected readonly promptBusy = signal(false);
  protected readonly copyNotice = signal<Notice | null>(null);
  protected readonly kind = signal<PromptKind>('adapter');

  /** Position de scroll du textarea, répercutée sur l'overlay de surlignage. */
  protected readonly scrollTop = signal(0);

  /** Mots-clés de l'offre déjà couverts par le texte courant (matching live). */
  private readonly coveredKeywords = computed(() =>
    (this.live()?.keywords ?? []).filter((k) => k.covered).map((k) => k.keyword),
  );

  /** Segments d'affichage (fond seulement) alignés sur le textarea éditable :
   *  vert = mot-clé couvert, teinte = ligne de section. Aucun gras (metrique). */
  protected readonly highlightSegments = computed(() =>
    buildHighlightSegments(this.store.adaptedText(), this.coveredKeywords()),
  );

  // --- Niveau clé API (niveau 2) -----------------------------------------
  protected readonly llmConfig = signal<LlmConfig | null>(null);
  protected readonly llmConfigError = signal(false);
  protected readonly keyInput = signal('');
  protected readonly savingKey = signal(false);
  /** Consentement explicite : coché à chaque session, jamais présumé. */
  protected readonly consent = signal(false);
  protected readonly adapting = signal(false);
  protected readonly apiNotice = signal<Notice | null>(null);

  protected readonly intents: readonly PromptIntent[] = [
    { kind: 'adapter', label: 'Adapter', hint: "Reformuler le CV pour l'offre (défaut)" },
    { kind: 'auditer', label: 'Auditer', hint: 'Critique de recruteur - ne réécrit rien' },
    { kind: 'muscler', label: 'Muscler', hint: "Verbes d'action, sans inventer de chiffres" },
    { kind: 'accrocher', label: 'Accrocher', hint: 'Accroche 3 lignes, que du vérifiable' },
  ];

  constructor() {
    // Matching en direct : recalcul (sans IA) à chaque pause de frappe. Un
    // échec ne tue jamais le flux (catchError > EMPTY) : le prochain caractère
    // relance le calcul, et l'écran dit que le score affiché n'est plus à jour.
    toObservable(this.store.adaptedText)
      .pipe(
        debounceTime(350),
        distinctUntilChanged(),
        switchMap((text) => {
          if (!text.trim()) return of(null);
          return this.store.liveMatch(text).pipe(
            catchError(() => {
              this.liveError.set(true);
              return EMPTY;
            }),
          );
        }),
        takeUntilDestroyed(),
      )
      .subscribe((result) => {
        this.liveError.set(false);
        this.live.set(result);
      });

    this.reloadLlmConfig();
  }

  private reloadLlmConfig(): void {
    this.llm
      .getConfig()
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: (config) => {
          this.llmConfig.set(config);
          this.llmConfigError.set(false);
        },
        error: () => {
          this.llmConfig.set(null);
          this.llmConfigError.set(true);
        },
      });
  }

  protected saveKey(): void {
    const key = this.keyInput().trim();
    if (!key || this.savingKey()) return;
    this.savingKey.set(true);
    this.apiNotice.set(null);
    this.llm
      .saveConfig(key)
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: (config) => {
          this.savingKey.set(false);
          this.keyInput.set(''); // la clé ne reste jamais dans le navigateur
          this.llmConfig.set(config);
          this.apiNotice.set(ok('Clé enregistrée sur ta machine (jamais dans le navigateur).'));
        },
        error: (err: unknown) => {
          this.savingKey.set(false);
          this.apiNotice.set(
            fail(describeError(err, "La clé n'a pas pu être enregistrée. Réessaie.")),
          );
        },
      });
  }

  protected removeKey(): void {
    if (!window.confirm('Retirer ta clé API de cette machine ?')) return;
    this.apiNotice.set(null);
    this.llm
      .removeConfig()
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: () => {
          this.consent.set(false);
          this.apiNotice.set(ok('Clé retirée de cette machine.'));
          this.reloadLlmConfig();
        },
        error: (err: unknown) =>
          this.apiNotice.set(fail(describeError(err, "La clé n'a pas pu être retirée. Réessaie."))),
      });
  }

  protected runAdapt(): void {
    if (this.adapting() || !this.consent() || !this.llmConfig()?.configured) return;
    this.adapting.set(true);
    this.apiNotice.set(null);
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
          this.apiNotice.set(
            ok(
              `Proposition de ${result.model} reçue - vérifie chaque changement dans l'Avant / Après.`,
            ),
          );
        },
        error: (err: unknown) => {
          this.adapting.set(false);
          this.apiNotice.set(
            fail(describeError(err, "L'appel à l'IA n'a pas abouti. Réessaie dans un instant.")),
          );
        },
      });
  }

  protected preparePrompt(): void {
    if (this.promptBusy()) return;
    this.promptBusy.set(true);
    this.copyNotice.set(null);
    this.store
      .buildPrompt(this.kind())
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: (result) => {
          this.promptText.set(result.prompt);
          this.promptBusy.set(false);
          this.copyNotice.set(ok('Prompt prêt ci-dessous - copie-le, puis colle-le dans ton IA.'));
        },
        error: (err: unknown) => {
          this.copyNotice.set(
            fail(describeError(err, "Le prompt n'a pas pu être préparé. Réessaie.")),
          );
          this.promptBusy.set(false);
        },
      });
  }

  protected async copyPrompt(): Promise<void> {
    try {
      await navigator.clipboard.writeText(this.promptText());
      this.copyNotice.set(ok('Copié - colle-le dans ton IA (Ctrl + V).'));
    } catch {
      this.copyNotice.set(
        fail(
          'Copie automatique impossible - sélectionne le texte ci-dessous et copie-le (Ctrl + C).',
        ),
      );
    }
  }

  protected resetAdapted(): void {
    this.store.adaptedText.set(this.store.cvText());
  }
}
