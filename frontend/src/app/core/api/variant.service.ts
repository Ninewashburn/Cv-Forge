import { HttpClient } from '@angular/common/http';
import { inject, Injectable } from '@angular/core';
import { Observable } from 'rxjs';

import { environment } from '../../../environments/environment';
import { CvVariant, CvVariantUpdate } from '../models';

@Injectable({ providedIn: 'root' })
export class VariantService {
  private readonly http = inject(HttpClient);
  private readonly base = `${environment.apiBaseUrl}/variants`;

  get(id: string): Observable<CvVariant> {
    return this.http.get<CvVariant>(`${this.base}/${id}`);
  }

  /** Enregistre le texte « après » validé dans l'Avant/Après. */
  update(id: string, data: CvVariantUpdate): Observable<CvVariant> {
    return this.http.patch<CvVariant>(`${this.base}/${id}`, data);
  }

  remove(id: string): Observable<void> {
    return this.http.delete<void>(`${this.base}/${id}`);
  }

  /** PDF propre et parsable du texte « après » validé (généré localement par le backend). */
  pdf(id: string): Observable<Blob> {
    return this.http.get(`${this.base}/${id}/pdf`, { responseType: 'blob' });
  }
}
