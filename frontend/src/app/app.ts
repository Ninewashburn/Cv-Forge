import { DatePipe } from '@angular/common';
import { ChangeDetectionStrategy, Component } from '@angular/core';

type WatchType = 'offer' | 'training' | 'news' | 'event' | 'application';
type WatchStatus =
  | 'bookmarked'
  | 'to_analyze'
  | 'ready'
  | 'applied'
  | 'follow_up'
  | 'registered'
  | 'read'
  | 'archived';

interface WatchItem {
  url: string;
  title: string;
  source: string;
  itemType: WatchType;
  capturedAt: string;
  status: WatchStatus;
  company?: string;
  tags: string[];
  relatedSkill?: string;
}

const SOURCE_LABELS: Partial<Record<string, string>> = {
  hellowork: 'Hellowork',
  indeed: 'Indeed',
  apec: 'APEC',
  'welcome-to-the-jungle': 'Welcome to the Jungle',
  linkedin: 'LinkedIn',
  'france-travail': 'France Travail',
  openclassrooms: 'OpenClassrooms',
  other: 'Autres',
};

const TYPE_LABELS: Record<WatchType, string> = {
  offer: 'Offres',
  training: 'Formations',
  news: 'News',
  event: 'Événements',
  application: 'Candidatures',
};

const STATUS_LABELS: Record<WatchStatus, string> = {
  bookmarked: 'Favori',
  to_analyze: 'À analyser',
  ready: 'Prête',
  applied: 'Postulée',
  follow_up: 'Relance',
  registered: 'Inscrit',
  read: 'Lu',
  archived: 'Archivé',
};

@Component({
  selector: 'cvforge-root',
  imports: [DatePipe],
  templateUrl: './app.html',
  styleUrl: './app.css',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class App {
  readonly title = 'Centre de veille candidature';
  readonly sourceLabels = SOURCE_LABELS;
  readonly typeLabels = TYPE_LABELS;
  readonly statusLabels = STATUS_LABELS;
  readonly sourceFilters = [
    'all',
    'hellowork',
    'indeed',
    'apec',
    'welcome-to-the-jungle',
    'linkedin',
    'france-travail',
    'other',
  ];
  readonly typeFilters: Array<'all' | WatchType> = [
    'all',
    'offer',
    'training',
    'news',
    'event',
    'application',
  ];
  readonly items: WatchItem[] = [
    {
      url: 'https://www.hellowork.com/fr-fr/emplois/123456.html',
      title: 'Développeur Full Stack Laravel Angular',
      company: 'Entreprise exemple',
      source: 'hellowork',
      itemType: 'offer',
      capturedAt: '2026-05-04T14:30:00',
      status: 'to_analyze',
      tags: ['laravel', 'angular', 'fullstack'],
    },
    {
      url: 'https://www.apec.fr/candidat/recherche-emploi.html/emploi/detail-offre/987654',
      title: 'Ingénieur logiciel Python',
      company: 'Studio produit',
      source: 'apec',
      itemType: 'offer',
      capturedAt: '2026-05-04T16:10:00',
      status: 'ready',
      tags: ['python', 'api', 'sql'],
    },
    {
      url: 'https://openclassrooms.com/fr/courses/angular',
      title: 'Approfondir Angular moderne',
      source: 'openclassrooms',
      itemType: 'training',
      capturedAt: '2026-05-05T08:40:00',
      status: 'bookmarked',
      tags: ['angular', 'frontend'],
      relatedSkill: 'Angular',
    },
    {
      url: 'https://www.linkedin.com/jobs/view/555555',
      title: 'Développeur Angular',
      company: 'SaaS locale',
      source: 'linkedin',
      itemType: 'application',
      capturedAt: '2026-05-05T09:15:00',
      status: 'applied',
      tags: ['angular', 'remote'],
    },
    {
      url: 'https://www.apec.fr/tendances-emploi',
      title: 'Tendances du marché développeur',
      source: 'apec',
      itemType: 'news',
      capturedAt: '2026-05-05T10:00:00',
      status: 'read',
      tags: ['veille', 'emploi'],
    },
  ];

  selectedSource = 'all';
  selectedType: 'all' | WatchType = 'all';

  get filteredItems(): WatchItem[] {
    return this.items.filter((item) => {
      const sourceMatches = this.selectedSource === 'all' || item.source === this.selectedSource;
      const typeMatches = this.selectedType === 'all' || item.itemType === this.selectedType;
      return sourceMatches && typeMatches;
    });
  }

  get offerCount(): number {
    return this.items.filter((item) => item.itemType === 'offer').length;
  }

  get applicationCount(): number {
    return this.items.filter((item) => item.itemType === 'application').length;
  }

  get learningCount(): number {
    return this.items.filter((item) => item.itemType === 'training').length;
  }

  sourceLabel(source: string): string {
    return this.sourceLabels[source] ?? source;
  }

  selectSource(source: string): void {
    this.selectedSource = source;
  }

  selectType(type: 'all' | WatchType): void {
    this.selectedType = type;
  }
}
