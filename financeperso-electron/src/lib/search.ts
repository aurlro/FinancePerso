// Search utilities for Command Palette
// Fuzzy search implementation with scoring

export type SearchItemType = 'transaction' | 'page' | 'action' | 'category';

export interface SearchItem {
  id: string;
  type: SearchItemType;
  title: string;
  subtitle?: string;
  icon: string;
  keywords?: string[];
  action: () => void;
  meta?: Record<string, unknown>;
}

export interface SearchResult extends SearchItem {
  score: number;
  matches: { start: number; end: number }[];
}

/**
 * Calculate Levenshtein distance between two strings
 */
function levenshteinDistance(a: string, b: string): number {
  const matrix: number[][] = [];

  for (let i = 0; i <= b.length; i++) {
    matrix[i] = [i];
  }

  for (let j = 0; j <= a.length; j++) {
    matrix[0][j] = j;
  }

  for (let i = 1; i <= b.length; i++) {
    for (let j = 1; j <= a.length; j++) {
      if (b.charAt(i - 1) === a.charAt(j - 1)) {
        matrix[i][j] = matrix[i - 1][j - 1];
      } else {
        matrix[i][j] = Math.min(
          matrix[i - 1][j - 1] + 1,
          matrix[i][j - 1] + 1,
          matrix[i - 1][j] + 1
        );
      }
    }
  }

  return matrix[b.length][a.length];
}

/**
 * Calculate fuzzy match score and positions
 */
function fuzzyMatch(query: string, text: string): { score: number; matches: { start: number; end: number }[] } | null {
  const queryLower = query.toLowerCase();
  const textLower = text.toLowerCase();
  
  // Exact match gets highest score
  if (textLower === queryLower) {
    return { score: 100, matches: [{ start: 0, end: text.length }] };
  }
  
  // Starts with query gets high score
  if (textLower.startsWith(queryLower)) {
    return { score: 90, matches: [{ start: 0, end: query.length }] };
  }
  
  // Contains query gets good score
  const index = textLower.indexOf(queryLower);
  if (index !== -1) {
    return { score: 70, matches: [{ start: index, end: index + query.length }] };
  }
  
  // Fuzzy matching - character by character
  let queryIdx = 0;
  let textIdx = 0;
  const matches: { start: number; end: number }[] = [];
  let matchStart = -1;
  
  while (queryIdx < query.length && textIdx < text.length) {
    if (queryLower[queryIdx] === textLower[textIdx]) {
      if (matchStart === -1) {
        matchStart = textIdx;
      }
      queryIdx++;
    } else if (matchStart !== -1) {
      matches.push({ start: matchStart, end: textIdx });
      matchStart = -1;
    }
    textIdx++;
  }
  
  if (matchStart !== -1) {
    matches.push({ start: matchStart, end: textIdx });
  }
  
  // If we matched all query characters
  if (queryIdx === query.length) {
    // Calculate score based on match quality
    const matchedChars = matches.reduce((sum, m) => sum + (m.end - m.start), 0);
    const coverage = matchedChars / text.length;
    const continuity = matches.length === 1 ? 20 : matches.length === 2 ? 10 : 0;
    const score = Math.floor(40 * coverage + continuity);
    
    return { score: Math.max(score, 10), matches };
  }
  
  // Check Levenshtein distance for typo tolerance
  if (query.length >= 3) {
    const distance = levenshteinDistance(queryLower, textLower.slice(0, Math.min(text.length, query.length + 2)));
    if (distance <= 2) {
      return { score: Math.max(5, 30 - distance * 10), matches: [{ start: 0, end: Math.min(text.length, query.length) }] };
    }
  }
  
  return null;
}

/**
 * Filter prefix for advanced search
 */
export interface SearchFilter {
  type?: SearchItemType;
  prefix?: string;
}

/**
 * Parse search query to extract filter prefix
 * Supports: /t (transactions), /p (pages), /a (actions), /c (categories)
 */
export function parseSearchQuery(query: string): { filter: SearchFilter; cleanQuery: string } {
  const trimmed = query.trim();
  
  if (trimmed.startsWith('/t ')) {
    return { filter: { type: 'transaction', prefix: '/t' }, cleanQuery: trimmed.slice(3) };
  }
  if (trimmed.startsWith('/p ')) {
    return { filter: { type: 'page', prefix: '/p' }, cleanQuery: trimmed.slice(3) };
  }
  if (trimmed.startsWith('/a ')) {
    return { filter: { type: 'action', prefix: '/a' }, cleanQuery: trimmed.slice(3) };
  }
  if (trimmed.startsWith('/c ')) {
    return { filter: { type: 'category', prefix: '/c' }, cleanQuery: trimmed.slice(3) };
  }
  
  return { filter: {}, cleanQuery: trimmed };
}

/**
 * Perform fuzzy search on items
 */
export function fuzzySearch(query: string, items: SearchItem[]): SearchResult[] {
  if (!query.trim()) {
    return items.map(item => ({ ...item, score: 0, matches: [] }));
  }
  
  const { filter, cleanQuery } = parseSearchQuery(query);
  
  if (!cleanQuery) {
    // Only filter by type, no text search
    return items
      .filter(item => !filter.type || item.type === filter.type)
      .map(item => ({ ...item, score: 0, matches: [] }));
  }
  
  const results: SearchResult[] = [];
  
  for (const item of items) {
    // Apply type filter
    if (filter.type && item.type !== filter.type) {
      continue;
    }
    
    // Search in title
    const titleMatch = fuzzyMatch(cleanQuery, item.title);
    
    // Search in subtitle
    const subtitleMatch = item.subtitle ? fuzzyMatch(cleanQuery, item.subtitle) : null;
    
    // Search in keywords
    let keywordMatch: { score: number; matches: { start: number; end: number }[] } | null = null;
    if (item.keywords) {
      for (const keyword of item.keywords) {
        const match = fuzzyMatch(cleanQuery, keyword);
        if (match && (!keywordMatch || match.score > keywordMatch.score)) {
          keywordMatch = match;
        }
      }
    }
    
    // Calculate best score
    let bestScore = 0;
    let bestMatches: { start: number; end: number }[] = [];
    
    if (titleMatch) {
      bestScore = titleMatch.score;
      bestMatches = titleMatch.matches;
    }
    
    if (subtitleMatch && subtitleMatch.score > bestScore) {
      bestScore = subtitleMatch.score * 0.8; // Slightly lower priority than title
      bestMatches = subtitleMatch.matches;
    }
    
    if (keywordMatch && keywordMatch.score > bestScore) {
      bestScore = keywordMatch.score * 0.6; // Lower priority for keywords
      bestMatches = [];
    }
    
    // Boost score based on type priority
    if (bestScore > 0) {
      const typeBoost: Record<SearchItemType, number> = {
        page: 5,
        action: 3,
        transaction: 2,
        category: 1,
      };
      bestScore += typeBoost[item.type] || 0;
      
      results.push({ ...item, score: bestScore, matches: bestMatches });
    }
  }
  
  // Sort by score descending
  return results.sort((a, b) => b.score - a.score);
}

/**
 * Highlight matched text
 */
export function highlightMatches(text: string, matches: { start: number; end: number }[]): React.ReactNode {
  if (!matches.length) return text;
  
  const parts: React.ReactNode[] = [];
  let lastEnd = 0;
  
  for (const match of matches) {
    // Add text before match
    if (match.start > lastEnd) {
      parts.push(text.slice(lastEnd, match.start));
    }
    
    // Add highlighted match
    parts.push(
      `<mark>${text.slice(match.start, match.end)}</mark>`
    );
    
    lastEnd = match.end;
  }
  
  // Add remaining text
  if (lastEnd < text.length) {
    parts.push(text.slice(lastEnd));
  }
  
  return parts.join('');
}

/**
 * Get filter label
 */
export function getFilterLabel(prefix: string): string {
  const labels: Record<string, string> = {
    '/t': 'Transactions',
    '/p': 'Pages',
    '/a': 'Actions',
    '/c': 'Catégories',
  };
  return labels[prefix] || 'Tous';
}
