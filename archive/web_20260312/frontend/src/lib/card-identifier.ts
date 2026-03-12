/**
 * Extracts a card identifier (e.g. "*1234") from a transaction label.
 * Matches patterns like: CB *1234, CB*1234, CARTE *1234, CARD *1234
 */
export function extractCardIdentifier(label: string): string | null {
  const match = label.match(/(?:CB|CARTE|CARD)\s?\*?\s?(\d{4})/i);
  if (!match) return null;
  return `*${match[1]}`;
}
