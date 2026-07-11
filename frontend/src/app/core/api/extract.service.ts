import { HttpClient } from '@angular/common/http';
import { inject, Injectable } from '@angular/core';
import { Observable } from 'rxjs';

import { environment } from '../../../environments/environment';
import { ExtractedText } from '../models';

@Injectable({ providedIn: 'root' })
export class ExtractService {
  private readonly http = inject(HttpClient);
  private readonly base = `${environment.apiBaseUrl}/extract`;

  /** Texte brut d'un fichier PDF ou texte — extraction 100 % locale, rien ne sort. */
  extract(file: File): Observable<ExtractedText> {
    const form = new FormData();
    form.append('file', file);
    return this.http.post<ExtractedText>(this.base, form);
  }
}
