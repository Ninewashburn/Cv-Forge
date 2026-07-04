import { HttpClient } from '@angular/common/http';
import { inject, Injectable } from '@angular/core';
import { Observable } from 'rxjs';

import { environment } from '../../../environments/environment';
import { MasterProfile, MasterProfileUpdate } from '../models';

@Injectable({ providedIn: 'root' })
export class ProfileService {
  private readonly http = inject(HttpClient);
  private readonly base = `${environment.apiBaseUrl}/profile`;

  /** Récupère le profil maître (créé vide au premier accès côté serveur). */
  get(): Observable<MasterProfile> {
    return this.http.get<MasterProfile>(this.base);
  }

  update(data: MasterProfileUpdate): Observable<MasterProfile> {
    return this.http.put<MasterProfile>(this.base, data);
  }
}
