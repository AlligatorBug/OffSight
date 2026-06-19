/**
 * Mirrors the label priority in backend/pipeline/annotator.py's _get_label:
 *   1. Player name  → "Messi"
 *   2. Jersey number → "#10"
 *   3. Tracker ID    → "ID 3"
 */
export function classifyLabel(label) {
  if (!label) return 'idonly';
  if (label.startsWith('#')) return 'numonly';
  if (label.startsWith('ID ')) return 'idonly';
  return 'named';
}