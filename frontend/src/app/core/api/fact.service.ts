import { HttpClient } from '@angular/common/http';
import { inject, Injectable } from '@angular/core';
import { Observable } from 'rxjs';

import { environment } from '../../../environments/environment';
import { Fact, FactCreate, FactUpdate } from '../models';

@Injectable({ providedIn: 'root' })
export class FactService {
  private readonly http = inject(HttpClient);
  private readonly base = `${environment.apiBaseUrl}/facts`;

  list(): Observable<Fact[]> {
    return this.http.get<Fact[]>(this.base);
  }

  get(id: string): Observable<Fact> {
    return this.http.get<Fact>(`${this.base}/${id}`);
  }

  create(data: FactCreate): Observable<Fact> {
    return this.http.post<Fact>(this.base, data);
  }

  update(id: string, data: FactUpdate): Observable<Fact> {
    return this.http.patch<Fact>(`${this.base}/${id}`, data);
  }

  /** Soft delete côté serveur (la ligne n'est jamais supprimée physiquement). */
  remove(id: string): Observable<void> {
    return this.http.delete<void>(`${this.base}/${id}`);
  }
}
