/** Déclenche l'enregistrement d'un fichier par le navigateur (PDF, sauvegarde ZIP...). */
export function downloadBlob(blob: Blob, filename: string): void {
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement('a');
  anchor.href = url;
  anchor.download = filename;
  anchor.click();
  URL.revokeObjectURL(url);
}

/** Nom de fichier sûr à partir d'un titre libre (accents retirés, ponctuation en tirets). */
export function fileSlug(title: string, fallback: string): string {
  return (
    title
      .normalize('NFD')
      .replace(/[\u0300-\u036f]/g, '')
      .replace(/[^A-Za-z0-9]+/g, '-')
      .replace(/^-+|-+$/g, '')
      .slice(0, 60) || fallback
  );
}
