import { useState, useCallback, useEffect, useMemo } from 'react';
import type { SearchItem, SearchResult, SearchItemType } from '@/lib/search';

const RECENT_SEARCHES_KEY = 'financeperso_recent_searches';
const MAX_RECENT_SEARCHES = 10;

export interface UseCommandPaletteReturn {
  isOpen: boolean;
  open: () => void;
  close: () => void;
  toggle: () => void;
  searchQuery: string;
  setSearchQuery: (query: string) => void;
  results: SearchResult[];
  selectedIndex: number;
  setSelectedIndex: (index: number) => void;
  recentSearches: string[];
  addToRecent: (query: string) => void;
  clearRecent: () => void;
  selectNext: () => void;
  selectPrev: () => void;
  executeSelected: () => void;
  activeFilter: SearchItemType | null;
}

export function useCommandPalette(allItems: SearchItem[]): UseCommandPaletteReturn {
  const [isOpen, setIsOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedIndex, setSelectedIndex] = useState(0);
  const [recentSearches, setRecentSearches] = useState<string[]>([]);

  // Load recent searches from localStorage on mount
  useEffect(() => {
    try {
      const stored = localStorage.getItem(RECENT_SEARCHES_KEY);
      if (stored) {
        setRecentSearches(JSON.parse(stored));
      }
    } catch {
      // Ignore localStorage errors
    }
  }, []);

  // Save recent searches to localStorage
  const saveRecentSearches = useCallback((searches: string[]) => {
    try {
      localStorage.setItem(RECENT_SEARCHES_KEY, JSON.stringify(searches));
    } catch {
      // Ignore localStorage errors
    }
  }, []);

  const open = useCallback(() => {
    setIsOpen(true);
    setSelectedIndex(0);
  }, []);

  const close = useCallback(() => {
    setIsOpen(false);
    setSearchQuery('');
    setSelectedIndex(0);
  }, []);

  const toggle = useCallback(() => {
    if (isOpen) {
      close();
    } else {
      open();
    }
  }, [isOpen, open, close]);

  const addToRecent = useCallback((query: string) => {
    if (!query.trim()) return;
    
    setRecentSearches(prev => {
      const filtered = prev.filter(s => s.toLowerCase() !== query.toLowerCase());
      const updated = [query, ...filtered].slice(0, MAX_RECENT_SEARCHES);
      saveRecentSearches(updated);
      return updated;
    });
  }, [saveRecentSearches]);

  const clearRecent = useCallback(() => {
    setRecentSearches([]);
    saveRecentSearches([]);
  }, [saveRecentSearches]);

  // Import fuzzySearch dynamically to avoid circular dependency
  const results = useMemo<SearchResult[]>(() => {
    if (!isOpen) return [];
    
    // Dynamic import to avoid circular dependency
    const { fuzzySearch } = require('@/lib/search');
    return fuzzySearch(searchQuery, allItems);
  }, [isOpen, searchQuery, allItems]);

  // Reset selection when results change
  useEffect(() => {
    setSelectedIndex(0);
  }, [searchQuery]);

  const selectNext = useCallback(() => {
    setSelectedIndex(prev => (prev + 1) % Math.max(results.length, 1));
  }, [results.length]);

  const selectPrev = useCallback(() => {
    setSelectedIndex(prev => (prev - 1 + Math.max(results.length, 1)) % Math.max(results.length, 1));
  }, [results.length]);

  const executeSelected = useCallback(() => {
    if (results.length > 0 && selectedIndex < results.length) {
      const item = results[selectedIndex];
      addToRecent(searchQuery || item.title);
      item.action();
      close();
    }
  }, [results, selectedIndex, searchQuery, addToRecent, close]);

  // Extract active filter from search query
  const activeFilter = useMemo<SearchItemType | null>(() => {
    const trimmed = searchQuery.trim();
    if (trimmed.startsWith('/t ')) return 'transaction';
    if (trimmed.startsWith('/p ')) return 'page';
    if (trimmed.startsWith('/a ')) return 'action';
    if (trimmed.startsWith('/c ')) return 'category';
    return null;
  }, [searchQuery]);

  // Keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Cmd+K / Ctrl+K to open
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault();
        toggle();
      }
      
      // Only handle these when palette is open
      if (!isOpen) return;
      
      switch (e.key) {
        case 'Escape':
          e.preventDefault();
          close();
          break;
        case 'ArrowDown':
          e.preventDefault();
          selectNext();
          break;
        case 'ArrowUp':
          e.preventDefault();
          selectPrev();
          break;
        case 'Enter':
          e.preventDefault();
          executeSelected();
          break;
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, toggle, close, selectNext, selectPrev, executeSelected]);

  return {
    isOpen,
    open,
    close,
    toggle,
    searchQuery,
    setSearchQuery,
    results,
    selectedIndex,
    setSelectedIndex,
    recentSearches,
    addToRecent,
    clearRecent,
    selectNext,
    selectPrev,
    executeSelected,
    activeFilter,
  };
}
