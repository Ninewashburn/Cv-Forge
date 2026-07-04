import { ChangeDetectionStrategy, Component } from '@angular/core';
import { RouterLink } from '@angular/router';

/**
 * Atelier (parcours guidé) — placeholder Phase 3.
 * Les étapes Sources → Analyse → Adaptation → Avant/Après → Export sont
 * implémentées en Phase 4, branchées sur les services core/api déjà prêts.
 */
@Component({
  selector: 'cvforge-wizard',
  imports: [RouterLink],
  templateUrl: './wizard.html',
  styleUrl: './wizard.css',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class Wizard {
  readonly steps = [
    { n: '01', label: 'Sources', detail: 'Importer / coller offre + CV (+ LinkedIn)' },
    { n: '02', label: 'Analyse', detail: 'Matching mots-clés, sans IA' },
    { n: '03', label: 'Adaptation', detail: 'Manuelle, copilote ou clé API' },
    { n: '04', label: 'Avant / Après', detail: 'Chaque ajout confirmé « vrai et prouvable »' },
    { n: '05', label: 'Export', detail: 'PDF propre + micro-suivi' },
  ];
}
