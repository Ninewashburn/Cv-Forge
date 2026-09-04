/** Message d'état montré à l'utilisateur : une confirmation OU une erreur,
 *  jamais les deux dans le même gris discret. L'erreur se voit. */
export interface Notice {
  readonly tone: 'ok' | 'error';
  readonly text: string;
}

export const ok = (text: string): Notice => ({ tone: 'ok', text });
export const fail = (text: string): Notice => ({ tone: 'error', text });
