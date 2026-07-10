import { HttpClient } from '@angular/common/http';
import { inject, Injectable } from '@angular/core';
import { Observable } from 'rxjs';

import { environment } from '../../../environments/environment';
import { Application, ApplicationCreate, ApplicationUpdate } from '../models';

@Injectable({ providedIn: 'root' })
export class ApplicationService {
  private readonly http = inject(HttpClient);
  private readonly base = `${environment.apiBaseUrl}/applications`;

  list(): Observable<Application[]> {
    return this.http.get<Application[]>(this.base);
  }

  create(data: ApplicationCreate): Observable<Application> {
    return this.http.post<Application>(this.base, data);
  }

  update(id: string, data: ApplicationUpdate): Observable<Application> {
    return this.http.patch<Application>(`${this.base}/${id}`, data);
  }

  remove(id: string): Observable<void> {
    return this.http.delete<void>(`${this.base}/${id}`);
  }
}
