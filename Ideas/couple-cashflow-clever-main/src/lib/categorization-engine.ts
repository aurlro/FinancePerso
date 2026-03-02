import type { CategorizationRule } from "@/hooks/useRules";

export interface TransactionDraft {
  date: string;
  label: string;
  amount: number;
  import_hash: string;
  category_id: string | null;
  is_internal_transfer: boolean;
  matched_transfer_id: string | null;
}

/**
 * Apply categorization rules (sorted by priority desc) to a label.
 * Returns the category_id of the first matching rule, or null.
 */
export function categorize(
  label: string,
  rules: CategorizationRule[]
): string | null {
  for (const rule of rules) {
    if (!rule.is_active) continue;
    try {
      const re = new RegExp(rule.regex_pattern, "i");
      if (re.test(label)) return rule.category_id;
    } catch {
      // skip invalid regex
    }
  }
  return null;
}

/**
 * Detect internal transfers: two transactions on different accounts
 * with inverse amounts and dates within 3 days of each other.
 */
export function detectInternalTransfers(
  drafts: { date: string; amount: number; bank_account_id: string; index: number }[]
): Set<number> {
  const transferIndices = new Set<number>();
  const sorted = [...drafts].sort((a, b) => a.date.localeCompare(b.date));

  for (let i = 0; i < sorted.length; i++) {
    if (transferIndices.has(sorted[i].index)) continue;
    for (let j = i + 1; j < sorted.length; j++) {
      if (transferIndices.has(sorted[j].index)) continue;
      // Different accounts
      if (sorted[i].bank_account_id === sorted[j].bank_account_id) continue;
      // Inverse amounts (within 0.01 tolerance)
      if (Math.abs(sorted[i].amount + sorted[j].amount) > 0.01) continue;
      // Within 3 days
      const d1 = new Date(sorted[i].date).getTime();
      const d2 = new Date(sorted[j].date).getTime();
      if (Math.abs(d1 - d2) > 3 * 86400000) continue;
      transferIndices.add(sorted[i].index);
      transferIndices.add(sorted[j].index);
      break;
    }
  }
  return transferIndices;
}

/** Generate a simple hash for dedup */
export function hashTransaction(date: string, label: string, amount: number): string {
  return `${date}|${label.trim().toLowerCase()}|${amount}`;
}
