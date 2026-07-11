import { HttpClient } from '@angular/common/http';
import { inject, Injectable } from '@angular/core';
import { Observable } from 'rxjs';

import { environment } from '../../../environments/environment';
import { LlmConfig } from '../models';

@Injectable({ providedIn: 'root' })
export class LlmService {
  private readonly http = inject(HttpClient);
  private readonly base = `${environment.apiBaseUrl}/llm`;

  /** État masqué de la configuration (la clé complète reste côté backend). */
  getConfig(): Observable<LlmConfig> {
    return this.http.get<LlmConfig>(`${this.base}/config`);
  }

  saveConfig(apiKey: string, model?: string): Observable<LlmConfig> {
    return this.http.put<LlmConfig>(`${this.base}/config`, {
      api_key: apiKey,
      model: model?.trim() || null,
    });
  }

  removeConfig(): Observable<void> {
    return this.http.delete<void>(`${this.base}/config`);
  }
}
