import { supabase } from "@/integrations/supabase/client";

// Stop words to ignore in French transaction labels
const STOP_WORDS = new Set([
  "carte", "virement", "paiement", "prelevement", "achat", "retrait",
  "par", "pour", "chez", "avec", "dans", "sur", "les", "des", "une",
  "qui", "que", "aux", "son", "ses", "notre", "nous", "vous", "leur",
  "pas", "plus", "tout", "tous", "cette", "mon", "votre", "fait",
  "bien", "peut", "dois", "avoir", "etre", "tres", "seul", "aussi",
]);

/**
 * Extract significant keywords from a transaction label.
 * Returns words > 3 chars, no digits/dates, not stop words.
 */
export function extractKeywords(label: string): string[] {
  return label
    .replace(/[^a-zA-ZÀ-ÿ\s]/g, " ") // remove non-letter chars
    .split(/\s+/)
    .map(w => w.toLowerCase().trim())
    .filter(w => w.length > 3)
    .filter(w => !STOP_WORDS.has(w))
    .filter(w => !/^\d+$/.test(w))
    // Deduplicate
    .filter((w, i, arr) => arr.indexOf(w) === i)
    .slice(0, 4); // max 4 keywords
}

/**
 * Build a case-insensitive regex pattern from keywords.
 * Uses (?=.*keyword) lookaheads so order doesn't matter.
 */
export function buildRegexPattern(keywords: string[]): string {
  if (keywords.length === 1) return `(?i)${keywords[0]}`;
  // Match all keywords in any order
  return keywords.map(k => `(?=.*${k})`).join("") + ".*";
}

/**
 * After a manual category change, auto-create a categorization rule
 * if no similar rule already exists for this label pattern.
 */
export async function maybeCreateAutoRule({
  label,
  categoryId,
  householdId,
}: {
  label: string;
  categoryId: string;
  householdId: string;
}): Promise<boolean> {
  const keywords = extractKeywords(label);
  if (keywords.length === 0) return false;

  const pattern = buildRegexPattern(keywords);

  // Check if a similar rule already exists for this category + pattern
  const { data: existing } = await supabase
    .from("categorization_rules")
    .select("id")
    .eq("household_id", householdId)
    .eq("category_id", categoryId)
    .eq("regex_pattern", pattern)
    .limit(1);

  if (existing && existing.length > 0) return false;

  const ruleName = `Auto: ${keywords[0]}`;

  const { error } = await supabase.from("categorization_rules").insert({
    household_id: householdId,
    category_id: categoryId,
    name: ruleName,
    regex_pattern: pattern,
    priority: 10,
    is_active: true,
  });

  return !error;
}

/**
 * After a manual attribution change, auto-create an attribution rule
 * if no similar rule already exists for this label pattern + member.
 */
export async function maybeCreateAutoAttributionRule({
  label,
  memberId,
  householdId,
}: {
  label: string;
  memberId: string;
  householdId: string;
}): Promise<boolean> {
  const keywords = extractKeywords(label);
  if (keywords.length === 0) return false;

  const pattern = buildRegexPattern(keywords);

  const { data: existing } = await supabase
    .from("attribution_rules")
    .select("id")
    .eq("household_id", householdId)
    .eq("member_id", memberId)
    .eq("regex_pattern", pattern)
    .limit(1);

  if (existing && existing.length > 0) return false;

  const ruleName = `Auto: ${keywords[0]}`;

  const { error } = await supabase.from("attribution_rules").insert({
    household_id: householdId,
    member_id: memberId,
    name: ruleName,
    regex_pattern: pattern,
    priority: 10,
    is_active: true,
  });

  return !error;
}
