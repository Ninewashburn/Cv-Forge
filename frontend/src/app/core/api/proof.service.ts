import { HttpClient } from '@angular/common/http';
import { inject, Injectable } from '@angular/core';
import { Observable } from 'rxjs';

import { environment } from '../../../environments/environment';
import { Proof, ProofCreate, ProofUpdate } from '../models';

@Injectable({ providedIn: 'root' })
export class ProofService {
  private readonly http = inject(HttpClient);
  private readonly base = `${environment.apiBaseUrl}/proofs`;

  list(): Observable<Proof[]> {
    return this.http.get<Proof[]>(this.base);
  }

  get(id: string): Observable<Proof> {
    return this.http.get<Proof>(`${this.base}/${id}`);
  }

  create(data: ProofCreate): Observable<Proof> {
    return this.http.post<Proof>(this.base, data);
  }

  update(id: string, data: ProofUpdate): Observable<Proof> {
    return this.http.patch<Proof>(`${this.base}/${id}`, data);
  }

  remove(id: string): Observable<void> {
    return this.http.delete<void>(`${this.base}/${id}`);
  }

  /** Attache la pièce jointe (une par preuve - remplace l'existante). 100 % local. */
  attachFile(id: string, file: File): Observable<Proof> {
    const form = new FormData();
    form.append('file', file);
    return this.http.put<Proof>(`${this.base}/${id}/file`, form);
  }

  /** URL de la pièce jointe (téléchargement direct par le navigateur). */
  fileUrl(id: string): string {
    return `${this.base}/${id}/file`;
  }
}
