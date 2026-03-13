import * as React from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  Search, 
  X, 
  Command, 
  FileText, 
  LayoutDashboard, 
  Wallet, 
  Target, 
  Folder, 
  Download, 
  CheckCircle, 
  Settings,
  TrendingUp,
  Zap,
  UserPlus,
  PlusCircle,
  Clock,
  ArrowRight,
  CreditCard,
  ShoppingCart,
  Car,
  Home,
  Gamepad2,
  Heart,
  Briefcase,
  Coffee
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { Dialog, DialogContent, DialogTitle } from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { useCommandPalette } from '@/hooks/useCommandPalette';
import type { SearchItem, SearchResult, SearchItemType } from '@/lib/search';
import { getFilterLabel, parseSearchQuery } from '@/lib/search';

// Icon mapping for dynamic icons
const iconMap: Record<string, React.ComponentType<{ className?: string }>> = {
  LayoutDashboard,
  Wallet,
  Target,
  Folder,
  Download,
  CheckCircle,
  Settings,
  FileText,
  TrendingUp,
  Zap,
  UserPlus,
  PlusCircle,
  Clock,
  CreditCard,
  ShoppingCart,
  Car,
  Home,
  Gamepad2,
  Heart,
  Briefcase,
  Coffee,
};

// Mock transactions data
const mockTransactions: SearchItem[] = [
  { id: 'tx-1', type: 'transaction', title: 'Carrefour Market', subtitle: '-45,67 € · Alimentation · 12 mars 2024', icon: 'ShoppingCart', keywords: ['courses', 'nourriture'], action: () => {} },
  { id: 'tx-2', type: 'transaction', title: 'TotalEnergies Station', subtitle: '-65,00 € · Transport · 10 mars 2024', icon: 'Car', keywords: ['essence', 'voiture'], action: () => {} },
  { id: 'tx-3', type: 'transaction', title: 'Netflix France', subtitle: '-13,49 € · Loisirs · 8 mars 2024', icon: 'Gamepad2', keywords: ['streaming', 'abonnement'], action: () => {} },
  { id: 'tx-4', type: 'transaction', title: 'EDF Facture', subtitle: '-89,50 € · Logement · 5 mars 2024', icon: 'Home', keywords: ['électricité', 'facture'], action: () => {} },
  { id: 'tx-5', type: 'transaction', title: 'Pharmacie du Centre', subtitle: '-23,40 € · Santé · 3 mars 2024', icon: 'Heart', keywords: ['médicaments', 'santé'], action: () => {} },
  { id: 'tx-6', type: 'transaction', title: 'Salaire Mars 2024', subtitle: '+3 200,00 € · Revenus · 1 mars 2024', icon: 'Briefcase', keywords: ['salaire', 'revenu'], action: () => {} },
  { id: 'tx-7', type: 'transaction', title: 'Starbucks', subtitle: '-5,80 € · Alimentation · 28 fév 2024', icon: 'Coffee', keywords: ['café', 'boisson'], action: () => {} },
  { id: 'tx-8', type: 'transaction', title: 'Decathlon', subtitle: '-129,99 € · Loisirs · 25 fév 2024', icon: 'Gamepad2', keywords: ['sport', 'achat'], action: () => {} },
  { id: 'tx-9', type: 'transaction', title: 'SNCF Connect', subtitle: '-45,00 € · Transport · 22 fév 2024', icon: 'Car', keywords: ['train', 'voyage'], action: () => {} },
  { id: 'tx-10', type: 'transaction', title: 'Loyer Mars 2024', subtitle: '-950,00 € · Logement · 1 mars 2024', icon: 'Home', keywords: ['loyer', 'maison'], action: () => {} },
];

// Mock categories
const mockCategories: SearchItem[] = [
  { id: 'cat-1', type: 'category', title: 'Alimentation', subtitle: 'Courses, restaurants, cafes', icon: 'ShoppingCart', keywords: ['nourriture', 'manger'], action: () => {} },
  { id: 'cat-2', type: 'category', title: 'Transport', subtitle: 'Essence, train, bus, taxi', icon: 'Car', keywords: ['voiture', 'déplacement'], action: () => {} },
  { id: 'cat-3', type: 'category', title: 'Logement', subtitle: 'Loyer, factures, charges', icon: 'Home', keywords: ['maison', 'appartement'], action: () => {} },
  { id: 'cat-4', type: 'category', title: 'Loisirs', subtitle: 'Sport, cinéma, abonnements', icon: 'Gamepad2', keywords: ['divertissement', 'hobbies'], action: () => {} },
  { id: 'cat-5', type: 'category', title: 'Santé', subtitle: 'Pharmacie, médecin, mutuelle', icon: 'Heart', keywords: ['médecine', 'soins'], action: () => {} },
];

// Generate all searchable items
function useSearchItems(): SearchItem[] {
  const navigate = useNavigate();

  return React.useMemo(() => {
    // Pages
    const pages: SearchItem[] = [
      { id: 'page-dashboard', type: 'page', title: 'Dashboard', subtitle: 'Vue d\'ensemble de vos finances', icon: 'LayoutDashboard', action: () => navigate('/') },
      { id: 'page-transactions', type: 'page', title: 'Transactions', subtitle: 'Liste de toutes vos transactions', icon: 'Wallet', action: () => navigate('/transactions') },
      { id: 'page-budgets', type: 'page', title: 'Budgets', subtitle: 'Gestion de vos budgets mensuels', icon: 'Target', action: () => navigate('/budgets') },
      { id: 'page-categories', type: 'page', title: 'Catégories', subtitle: 'Organisation par catégories', icon: 'Folder', action: () => navigate('/categories') },
      { id: 'page-import', type: 'page', title: 'Import', subtitle: 'Importer des transactions CSV', icon: 'Download', action: () => navigate('/import') },
      { id: 'page-validation', type: 'page', title: 'Validation', subtitle: 'Valider les transactions en attente', icon: 'CheckCircle', action: () => navigate('/validation') },
      { id: 'page-settings', type: 'page', title: 'Paramètres', subtitle: 'Configuration de l\'application', icon: 'Settings', action: () => navigate('/settings') },
    ];

    // Actions
    const actions: SearchItem[] = [
      { id: 'action-import', type: 'action', title: 'Importer CSV', subtitle: 'Importer un fichier de transactions', icon: 'Download', keywords: ['csv', 'fichier', 'upload'], action: () => navigate('/import') },
      { id: 'action-budget', type: 'action', title: 'Nouveau budget', subtitle: 'Créer un nouveau budget', icon: 'PlusCircle', keywords: ['créer', 'budget', 'ajouter'], action: () => navigate('/budgets') },
      { id: 'action-member', type: 'action', title: 'Ajouter membre', subtitle: 'Ajouter un membre au foyer', icon: 'UserPlus', keywords: ['personne', 'famille', 'couple'], action: () => navigate('/settings') },
      { id: 'action-categorize', type: 'action', title: 'Catégoriser automatiquement', subtitle: 'Lancer l\'IA de catégorisation', icon: 'Zap', keywords: ['ia', 'ai', 'auto'], action: () => navigate('/validation') },
      { id: 'action-reports', type: 'action', title: 'Voir rapports', subtitle: 'Accéder aux rapports détaillés', icon: 'TrendingUp', keywords: ['stats', 'analyse', 'graphiques'], action: () => navigate('/') },
    ];

    // Update mock transactions with navigation
    const transactionsWithActions = mockTransactions.map(tx => ({
      ...tx,
      action: () => navigate('/transactions'),
    }));

    // Update categories with navigation
    const categoriesWithActions = mockCategories.map(cat => ({
      ...cat,
      action: () => navigate('/categories'),
    }));

    return [...pages, ...actions, ...transactionsWithActions, ...categoriesWithActions];
  }, [navigate]);
}

// Render icon component
function renderIcon(iconName: string, className?: string) {
  const Icon = iconMap[iconName];
  if (Icon) {
    return <Icon className={className} />;
  }
  return <FileText className={className} />;
}

// Get icon for type
function getTypeIcon(type: SearchItemType) {
  switch (type) {
    case 'transaction':
      return <CreditCard className="h-4 w-4 text-blue-500" />;
    case 'page':
      return <LayoutDashboard className="h-4 w-4 text-emerald-500" />;
    case 'action':
      return <Zap className="h-4 w-4 text-amber-500" />;
    case 'category':
      return <Folder className="h-4 w-4 text-purple-500" />;
    default:
      return <FileText className="h-4 w-4 text-gray-500" />;
  }
}

// Get type label
function getTypeLabel(type: SearchItemType) {
  switch (type) {
    case 'transaction':
      return 'Transaction';
    case 'page':
      return 'Page';
    case 'action':
      return 'Action';
    case 'category':
      return 'Catégorie';
    default:
      return 'Résultat';
  }
}

// Highlight matches in text
function highlightText(text: string, query: string): React.ReactNode {
  if (!query.trim()) return text;
  
  const { cleanQuery } = parseSearchQuery(query);
  if (!cleanQuery) return text;
  
  const lowerText = text.toLowerCase();
  const lowerQuery = cleanQuery.toLowerCase();
  const index = lowerText.indexOf(lowerQuery);
  
  if (index === -1) return text;
  
  return (
    <>
      {text.slice(0, index)}
      <mark className="bg-emerald-200 text-emerald-900 rounded px-0.5">
        {text.slice(index, index + cleanQuery.length)}
      </mark>
      {text.slice(index + cleanQuery.length)}
    </>
  );
}

// Recent searches component
function RecentSearches({
  searches,
  onSelect,
  onClear,
}: {
  searches: string[];
  onSelect: (search: string) => void;
  onClear: () => void;
}) {
  if (searches.length === 0) return null;

  return (
    <div className="px-4 py-3 border-b border-gray-100">
      <div className="flex items-center justify-between mb-2">
        <span className="text-xs font-medium text-gray-500 uppercase tracking-wider">
          Recherches récentes
        </span>
        <Button
          variant="ghost"
          size="sm"
          onClick={onClear}
          className="h-auto py-1 px-2 text-xs text-gray-400 hover:text-gray-600"
        >
          Effacer
        </Button>
      </div>
      <div className="flex flex-wrap gap-2">
        {searches.map((search, idx) => (
          <button
            key={idx}
            onClick={() => onSelect(search)}
            className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-gray-100 text-sm text-gray-700 hover:bg-gray-200 transition-colors"
          >
            <Clock className="h-3 w-3 text-gray-400" />
            {search}
          </button>
        ))}
      </div>
    </div>
  );
}

// Filter hints component
function FilterHints() {
  const filters = [
    { prefix: '/t', label: 'transactions', example: '/t carrefour' },
    { prefix: '/p', label: 'pages', example: '/p budget' },
    { prefix: '/a', label: 'actions', example: '/a import' },
    { prefix: '/c', label: 'catégories', example: '/c alim' },
  ];

  return (
    <div className="px-4 py-3 border-t border-gray-100 bg-gray-50/50">
      <div className="flex items-center gap-4 text-xs text-gray-500">
        <span className="font-medium">Filtres rapides:</span>
        {filters.map((f) => (
          <div key={f.prefix} className="flex items-center gap-1">
            <code className="px-1.5 py-0.5 bg-gray-200 rounded text-gray-700 font-mono">
              {f.prefix}
            </code>
            <span>{f.label}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

// Empty state component
function EmptyState({ query }: { query: string }) {
  return (
    <div className="flex flex-col items-center justify-center py-12 px-4 text-center">
      <div className="h-12 w-12 rounded-full bg-gray-100 flex items-center justify-center mb-4">
        <Search className="h-6 w-6 text-gray-400" />
      </div>
      <h3 className="text-sm font-medium text-gray-900 mb-1">
        Aucun résultat trouvé
      </h3>
      <p className="text-sm text-gray-500 max-w-xs">
        Aucun résultat pour &quot;<span className="font-medium text-gray-700">{query}</span>&quot;.
        <br />
        Essayez avec d&apos;autres termes ou vérifiez l&apos;orthographe.
      </p>
    </div>
  );
}

interface CommandPaletteProps {
  open?: boolean;
  onOpenChange?: (open: boolean) => void;
}

// Main Command Palette Component
export function CommandPalette({ open: controlledOpen, onOpenChange }: CommandPaletteProps = {}) {
  const items = useSearchItems();
  const palette = useCommandPalette(items);
  
  // Use controlled state if provided, otherwise use internal state
  const isOpen = controlledOpen !== undefined ? controlledOpen : palette.isOpen;
  const close = () => {
    palette.close();
    onOpenChange?.(false);
  };
  const open = () => {
    palette.open();
    onOpenChange?.(true);
  };
  
  const {
    searchQuery,
    setSearchQuery,
    results,
    selectedIndex,
    setSelectedIndex,
    recentSearches,
    addToRecent,
    clearRecent,
    executeSelected,
    activeFilter,
  } = palette;

  const inputRef = React.useRef<HTMLInputElement>(null);

  // Focus input when opened
  React.useEffect(() => {
    if (isOpen) {
      setTimeout(() => inputRef.current?.focus(), 100);
    }
  }, [isOpen]);

  const handleSelect = (result: SearchResult) => {
    addToRecent(searchQuery || result.title);
    result.action();
    if (controlledOpen === undefined) {
      palette.close();
    }
    onOpenChange?.(false);
  };

  const handleRecentSelect = (search: string) => {
    setSearchQuery(search);
    inputRef.current?.focus();
  };

  // Group results by type
  const groupedResults = React.useMemo(() => {
    const groups: Record<string, SearchResult[]> = {};
    results.forEach((result) => {
      if (!groups[result.type]) {
        groups[result.type] = [];
      }
      groups[result.type].push(result);
    });
    return groups;
  }, [results]);

  // Order of types
  const typeOrder: SearchItemType[] = ['page', 'action', 'transaction', 'category'];

  const showRecent = !searchQuery.trim() && recentSearches.length > 0;

  return (
    <Dialog open={isOpen} onOpenChange={(newOpen) => {
      if (!newOpen) {
        close();
      } else {
        open();
      }
    }}>
      <DialogContent className="fixed inset-0 z-50 flex items-start justify-center pt-[10vh] p-0 border-0 bg-transparent shadow-none">
        <DialogTitle className="sr-only">Recherche globale</DialogTitle>
        {/* Backdrop */}
        <div 
          className="fixed inset-0 bg-black/30 backdrop-blur-sm transition-opacity"
          onClick={close}
          aria-hidden="true"
        />
        
        {/* Command Palette Container */}
        <div className="relative z-50 w-full max-w-2xl mx-4 animate-in fade-in zoom-in-95 duration-200">
          <div className="bg-white dark:bg-gray-900 rounded-xl shadow-2xl border border-gray-200 dark:border-gray-700 overflow-hidden flex flex-col max-h-[60vh]">
            {/* Search Input */}
            <div className="flex items-center gap-3 px-4 py-4 border-b border-gray-100 dark:border-gray-800">
              <Search className="h-5 w-5 text-gray-400 flex-shrink-0" />
              <Input
                ref={inputRef}
                type="text"
                placeholder="Rechercher..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="flex-1 border-0 bg-transparent p-0 text-base placeholder:text-gray-400 focus-visible:ring-0 focus-visible:ring-offset-0"
              />
              {activeFilter && (
                <span className="text-xs px-2 py-1 bg-emerald-100 text-emerald-700 rounded-full font-medium">
                  {getFilterLabel(searchQuery.slice(0, 2))}
                </span>
              )}
              <div className="flex items-center gap-1">
                <kbd className="hidden sm:inline-flex items-center gap-1 px-2 py-1 rounded bg-gray-100 dark:bg-gray-800 text-xs text-gray-500 font-mono">
                  <Command className="h-3 w-3" />
                  K
                </kbd>
                <button
                  onClick={close}
                  className="p-1.5 rounded hover:bg-gray-100 dark:hover:bg-gray-800 text-gray-400 hover:text-gray-600 transition-colors"
                >
                  <X className="h-4 w-4" />
                </button>
              </div>
            </div>

            {/* Recent Searches */}
            {showRecent && (
              <RecentSearches
                searches={recentSearches}
                onSelect={handleRecentSelect}
                onClear={clearRecent}
              />
            )}

            {/* Results List */}
            <div className="flex-1 overflow-y-auto">
              {results.length === 0 && searchQuery.trim() ? (
                <EmptyState query={searchQuery} />
              ) : results.length === 0 && !showRecent ? (
                <div className="flex flex-col items-center justify-center py-12 px-4 text-center">
                  <p className="text-sm text-gray-500">
                    Commencez à taper pour rechercher...
                  </p>
                </div>
              ) : (
                <div className="py-2">
                  {typeOrder.map((type) => {
                    const typeResults = groupedResults[type];
                    if (!typeResults || typeResults.length === 0) return null;

                    return (
                      <div key={type} className="mb-2">
                        <div className="px-4 py-1.5 text-xs font-medium text-gray-500 uppercase tracking-wider flex items-center gap-2">
                          {getTypeIcon(type)}
                          {getTypeLabel(type)}s
                          <span className="text-gray-400">({typeResults.length})</span>
                        </div>
                        {typeResults.map((result, idx) => {
                          const globalIndex = results.findIndex(r => r.id === result.id);
                          const isSelected = globalIndex === selectedIndex;

                          return (
                            <button
                              key={result.id}
                              onClick={() => handleSelect(result)}
                              onMouseEnter={() => setSelectedIndex(globalIndex)}
                              className={cn(
                                "w-full flex items-center gap-3 px-4 py-3 text-left transition-colors",
                                isSelected
                                  ? "bg-emerald-50 dark:bg-emerald-900/20"
                                  : "hover:bg-gray-50 dark:hover:bg-gray-800/50"
                              )}
                            >
                              <div className={cn(
                                "h-10 w-10 rounded-lg flex items-center justify-center flex-shrink-0",
                                isSelected ? "bg-emerald-100 dark:bg-emerald-800" : "bg-gray-100 dark:bg-gray-800"
                              )}>
                                {renderIcon(result.icon, cn(
                                  "h-5 w-5",
                                  isSelected ? "text-emerald-600 dark:text-emerald-400" : "text-gray-500 dark:text-gray-400"
                                ))}
                              </div>
                              <div className="flex-1 min-w-0">
                                <div className={cn(
                                  "font-medium truncate",
                                  isSelected ? "text-emerald-900 dark:text-emerald-100" : "text-gray-900 dark:text-gray-100"
                                )}>
                                  {highlightText(result.title, searchQuery)}
                                </div>
                                {result.subtitle && (
                                  <div className="text-sm text-gray-500 dark:text-gray-400 truncate">
                                    {highlightText(result.subtitle, searchQuery)}
                                  </div>
                                )}
                              </div>
                              {isSelected && (
                                <ArrowRight className="h-4 w-4 text-emerald-500 flex-shrink-0" />
                              )}
                            </button>
                          );
                        })}
                      </div>
                    );
                  })}
                </div>
              )}
            </div>

            {/* Footer with hints */}
            {!searchQuery.trim() && <FilterHints />}
            
            {/* Results count */}
            {results.length > 0 && (
              <div className="px-4 py-2 border-t border-gray-100 dark:border-gray-800 bg-gray-50/50 dark:bg-gray-900/50 flex items-center justify-between text-xs text-gray-500">
                <span>
                  {results.length} résultat{results.length > 1 ? 's' : ''}
                </span>
                <div className="flex items-center gap-3">
                  <span className="flex items-center gap-1">
                    <kbd className="px-1.5 py-0.5 bg-gray-200 dark:bg-gray-700 rounded text-gray-600 dark:text-gray-300 font-mono">↑↓</kbd>
                    naviguer
                  </span>
                  <span className="flex items-center gap-1">
                    <kbd className="px-1.5 py-0.5 bg-gray-200 dark:bg-gray-700 rounded text-gray-600 dark:text-gray-300 font-mono">↵</kbd>
                    sélectionner
                  </span>
                </div>
              </div>
            )}
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}

// Trigger button component for header
export function CommandPaletteTrigger({ onClick }: { onClick: () => void }) {
  return (
    <Button
      variant="outline"
      size="sm"
      onClick={onClick}
      className="hidden sm:flex items-center gap-2 text-gray-500 hover:text-gray-700 bg-gray-50 hover:bg-gray-100 border-gray-200"
    >
      <Search className="h-4 w-4" />
      <span className="text-sm">Rechercher...</span>
      <kbd className="ml-2 hidden lg:inline-flex items-center gap-1 px-1.5 py-0.5 rounded bg-white border text-xs text-gray-400 font-mono">
        <Command className="h-3 w-3" />
        K
      </kbd>
    </Button>
  );
}

// Mobile trigger (icon only)
export function CommandPaletteTriggerMobile({ onClick }: { onClick: () => void }) {
  return (
    <Button
      variant="ghost"
      size="icon"
      onClick={onClick}
      className="sm:hidden"
      aria-label="Rechercher"
    >
      <Search className="h-5 w-5" />
    </Button>
  );
}

export default CommandPalette;
