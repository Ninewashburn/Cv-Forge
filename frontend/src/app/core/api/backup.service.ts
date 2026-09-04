import { HttpClient } from '@angular/common/http';
import { inject, Injectable } from '@angular/core';
import { Observable } from 'rxjs';

import { environment } from '../../../environments/environment';

@Injectable({ providedIn: 'root' })
export class BackupService {
  private readonly http = inject(HttpClient);
  private readonly base = `${environment.apiBaseUrl}/backup`;

  /** Archive ZIP complète (base + fichiers de preuves), reçue comme un fichier
   *  pour que l'écran puisse dire clairement si ça a marché ou non. */
  export(): Observable<Blob> {
    return this.http.get(`${this.base}/export`, { responseType: 'blob' });
  }

  /** Restaure une sauvegarde : remplace TOUTES les données locales. */
  import(file: File): Observable<void> {
    const form = new FormData();
    form.append('file', file);
    return this.http.post<void>(`${this.base}/import`, form);
  }
}
