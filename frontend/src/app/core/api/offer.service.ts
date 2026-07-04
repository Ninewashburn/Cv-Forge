import { HttpClient } from '@angular/common/http';
import { inject, Injectable } from '@angular/core';
import { Observable } from 'rxjs';

import { environment } from '../../../environments/environment';
import {
  CopilotPrompt,
  CopilotPromptRequest,
  CvVariant,
  MatchRequest,
  MatchingResult,
  Offer,
  OfferCreate,
  OfferUpdate,
} from '../models';

@Injectable({ providedIn: 'root' })
export class OfferService {
  private readonly http = inject(HttpClient);
  private readonly base = `${environment.apiBaseUrl}/offers`;

  list(): Observable<Offer[]> {
    return this.http.get<Offer[]>(this.base);
  }

  get(id: string): Observable<Offer> {
    return this.http.get<Offer>(`${this.base}/${id}`);
  }

  /** Crée l'offre : l'analyse (mots-clés, missions) est calculée côté serveur. */
  create(data: OfferCreate): Observable<Offer> {
    return this.http.post<Offer>(this.base, data);
  }

  update(id: string, data: OfferUpdate): Observable<Offer> {
    return this.http.patch<Offer>(`${this.base}/${id}`, data);
  }

  remove(id: string): Observable<void> {
    return this.http.delete<void>(`${this.base}/${id}`);
  }

  analyze(id: string): Observable<Offer> {
    return this.http.post<Offer>(`${this.base}/${id}/analyze`, {});
  }

  /** Couverture des mots-clés par un texte (absent → profil maître). Sans LLM. */
  matching(id: string, body: MatchRequest = {}): Observable<MatchingResult> {
    return this.http.post<MatchingResult>(`${this.base}/${id}/matching`, body);
  }

  /** Prompt verrouillé anti-hallucination (kind : adapter/auditer/muscler/accrocher). */
  copilotPrompt(id: string, body: CopilotPromptRequest = {}): Observable<CopilotPrompt> {
    return this.http.post<CopilotPrompt>(`${this.base}/${id}/copilot-prompt`, body);
  }

  generateVariant(id: string): Observable<CvVariant> {
    return this.http.post<CvVariant>(`${this.base}/${id}/variants`, {});
  }

  listVariants(id: string): Observable<CvVariant[]> {
    return this.http.get<CvVariant[]>(`${this.base}/${id}/variants`);
  }
}
