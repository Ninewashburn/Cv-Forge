import { HttpClient } from '@angular/common/http';
import { inject, Injectable } from '@angular/core';
import { Observable } from 'rxjs';

import { environment } from '../../../environments/environment';

@Injectable({ providedIn: 'root' })
export class BackupService {
  private readonly http = inject(HttpClient);
  private readonly base = `${environment.apiBaseUrl}/backup`;

  /** URL de téléchargement direct (le navigateur gère le fichier). */
  readonly exportUrl = `${this.base}/export`;

  /** Restaure un backup : remplace TOUTES les données locales. */
  import(file: File): Observable<void> {
    const form = new FormData();
    form.append('file', file);
    return this.http.post<void>(`${this.base}/import`, form);
  }
}
