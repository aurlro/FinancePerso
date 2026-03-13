import * as React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Checkbox } from '@/components/ui/checkbox';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { 
  CheckCircle2, 
  XCircle, 
  AlertCircle, 
  ChevronDown, 
  ChevronUp,
  CheckSquare,
  Square,
  EyeOff,
  Sparkles,
  Brain,
  Loader2,
  Zap,
  Wand2
} from 'lucide-react';
import { useValidation } from '@/hooks/useValidation';
import { useCategories } from '@/hooks/useTransactions';
import { useAI, type CategorizationResult } from '@/hooks/useAI';
import type { Transaction } from '@/types';

interface TransactionGroup {
  pattern: string;
  transactions: Transaction[];
  selectedCategory: string;
  ignoredIds: Set<number>;
  suggestedCategory?: string;
  suggestionConfidence?: number;
  suggestionSource?: string;
}

// Fonction pour extraire le pattern d'une description
function extractPattern(description: string): string {
  return description
    .toUpperCase()
    .replace(/\d+/g, '') // Supprime les nombres
    .replace(/\b\d{5}\b/g, '') // Supprime les codes postaux
    .replace(/\s+/g, ' ') // Normalise les espaces
    .trim()
    .split(' ')
    .slice(0, 3) // Prend les 3 premiers mots significatifs
    .join(' ');
}

// Groupe les transactions par pattern similaire
function groupTransactions(transactions: Transaction[]): TransactionGroup[] {
  const groups = new Map<string, Transaction[]>();

  for (const tx of transactions) {
    const pattern = extractPattern(tx.description);
    if (!groups.has(pattern)) {
      groups.set(pattern, []);
    }
    groups.get(pattern)!.push(tx);
  }

  return Array.from(groups.entries())
    .map(([pattern, txs]) => ({
      pattern,
      transactions: txs,
      selectedCategory: '',
      ignoredIds: new Set<number>(),
    }))
    .sort((a, b) => b.transactions.length - a.transactions.length);
}

/**
 * Retourne la couleur associée à une catégorie
 */
function getCategoryColor(category: string): string {
  const colors: Record<string, string> = {
    'Alimentation': 'bg-green-100 text-green-800 border-green-200',
    'Transport': 'bg-blue-100 text-blue-800 border-blue-200',
    'Logement': 'bg-purple-100 text-purple-800 border-purple-200',
    'Santé': 'bg-red-100 text-red-800 border-red-200',
    'Loisirs': 'bg-amber-100 text-amber-800 border-amber-200',
    'Shopping': 'bg-pink-100 text-pink-800 border-pink-200',
    'Restauration': 'bg-orange-100 text-orange-800 border-orange-200',
    'Revenus': 'bg-emerald-100 text-emerald-800 border-emerald-200',
    'Assurances': 'bg-cyan-100 text-cyan-800 border-cyan-200',
    'Banque': 'bg-gray-100 text-gray-800 border-gray-200',
    'Impôts': 'bg-slate-100 text-slate-800 border-slate-200',
    'Télécom': 'bg-indigo-100 text-indigo-800 border-indigo-200',
    'Épargne': 'bg-rose-100 text-rose-800 border-rose-200',
    'Inconnu': 'bg-gray-100 text-gray-600 border-gray-200',
  };
  return colors[category] || 'bg-gray-100 text-gray-800 border-gray-200';
}

/**
 * Retourne l'icône associée à la source de suggestion
 */
function getSourceIcon(source?: string) {
  switch (source) {
    case 'ai':
      return <Brain className="h-3 w-3" />;
    case 'rule':
      return <Zap className="h-3 w-3" />;
    case 'fallback':
      return <Sparkles className="h-3 w-3" />;
    default:
      return null;
  }
}

export function Validation() {
  const { pendingTransactions, loading, error, refresh, validateBatch, ignoreTransactions } = useValidation();
  const { categories } = useCategories();
  const { categorize, settings: aiSettings, loading: aiLoading } = useAI();
  
  const [groups, setGroups] = React.useState<TransactionGroup[]>([]);
  const [expandedGroups, setExpandedGroups] = React.useState<Set<string>>(new Set());
  const [validating, setValidating] = React.useState(false);
  const [categorizingAll, setCategorizingAll] = React.useState(false);
  const [categorizedCount, setCategorizedCount] = React.useState(0);

  // Regroupe les transactions quand elles changent
  React.useEffect(() => {
    if (pendingTransactions.length > 0) {
      setGroups(groupTransactions(pendingTransactions));
    } else {
      setGroups([]);
    }
  }, [pendingTransactions]);

  const toggleGroup = (pattern: string) => {
    const newExpanded = new Set(expandedGroups);
    if (newExpanded.has(pattern)) {
      newExpanded.delete(pattern);
    } else {
      newExpanded.add(pattern);
    }
    setExpandedGroups(newExpanded);
  };

  const handleCategoryChange = (pattern: string, category: string) => {
    setGroups(prev => prev.map(g => 
      g.pattern === pattern ? { ...g, selectedCategory: category } : g
    ));
  };

  const toggleIgnoreTransaction = (pattern: string, id: number) => {
    setGroups(prev => prev.map(g => {
      if (g.pattern !== pattern) return g;
      const newIgnored = new Set(g.ignoredIds);
      if (newIgnored.has(id)) {
        newIgnored.delete(id);
      } else {
        newIgnored.add(id);
      }
      return { ...g, ignoredIds: newIgnored };
    }));
  };

  const handleValidateGroup = async (group: TransactionGroup) => {
    if (!group.selectedCategory) return;
    
    const ids = group.transactions
      .filter(tx => !group.ignoredIds.has(tx.id))
      .map(tx => tx.id);
    
    if (ids.length === 0) return;

    setValidating(true);
    try {
      await validateBatch(ids, group.selectedCategory);
      refresh();
    } catch (err) {
      console.error('Failed to validate group:', err);
    } finally {
      setValidating(false);
    }
  };

  const handleValidateAll = async () => {
    setValidating(true);
    try {
      // Valide par groupe pour maintenir la cohérence
      for (const group of groups) {
        if (!group.selectedCategory) continue;
        await handleValidateGroup(group);
      }
      refresh();
    } catch (err) {
      console.error('Failed to validate all:', err);
    } finally {
      setValidating(false);
    }
  };

  const handleIgnoreSelected = async () => {
    const idsToIgnore: number[] = [];
    for (const group of groups) {
      idsToIgnore.push(...Array.from(group.ignoredIds));
    }

    if (idsToIgnore.length === 0) return;

    try {
      await ignoreTransactions(idsToIgnore);
      refresh();
    } catch (err) {
      console.error('Failed to ignore transactions:', err);
    }
  };

  /**
   * Catégorise un groupe avec l'IA
   */
  const categorizeGroup = async (group: TransactionGroup) => {
    if (group.transactions.length === 0) return;
    
    // Utilise la première transaction du groupe comme référence
    const sampleTx = group.transactions[0];
    const result = await categorize(sampleTx.description, sampleTx.amount);
    
    if (result) {
      setGroups(prev => prev.map(g => 
        g.pattern === group.pattern 
          ? { 
              ...g, 
              selectedCategory: result.category,
              suggestedCategory: result.category,
              suggestionConfidence: result.confidence,
              suggestionSource: result.source
            } 
          : g
      ));
    }
  };

  /**
   * Catégorise tous les groupes avec l'IA
   */
  const categorizeAll = async () => {
    setCategorizingAll(true);
    setCategorizedCount(0);
    
    try {
      // Ne catégoriser que les groupes sans catégorie sélectionnée
      const groupsToCategorize = groups.filter(g => !g.selectedCategory);
      
      for (let i = 0; i < groupsToCategorize.length; i++) {
        const group = groupsToCategorize[i];
        await categorizeGroup(group);
        setCategorizedCount(i + 1);
        
        // Petit délai pour éviter de surcharger l'API et permettre l'affichage
        if (i < groupsToCategorize.length - 1) {
          await new Promise(resolve => setTimeout(resolve, 200));
        }
      }
    } catch (err) {
      console.error('Failed to categorize all:', err);
    } finally {
      setCategorizingAll(false);
      setCategorizedCount(0);
    }
  };

  const totalPending = pendingTransactions.length;
  const groupsWithCategory = groups.filter(g => g.selectedCategory).length;
  const canValidateAll = groupsWithCategory > 0;
  const uncategorizedGroups = groups.filter(g => !g.selectedCategory).length;

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-emerald-600" />
      </div>
    );
  }

  if (error) {
    return (
      <Alert variant="destructive">
        <AlertCircle className="h-4 w-4" />
        <AlertTitle>Erreur</AlertTitle>
        <AlertDescription>{error}</AlertDescription>
      </Alert>
    );
  }

  if (totalPending === 0) {
    return (
      <div className="space-y-4">
        <h2 className="text-2xl font-bold">Validation des transactions</h2>
        <Card>
          <CardContent className="p-12">
            <div className="text-center space-y-4">
              <CheckCircle2 className="h-16 w-16 text-emerald-500 mx-auto" />
              <h3 className="text-xl font-semibold text-gray-900">
                Toutes les transactions sont catégorisées !
              </h3>
              <p className="text-gray-500 max-w-md mx-auto">
                Il n'y a aucune transaction en attente de validation. 
                Importez de nouvelles transactions ou modifiez des catégories existantes.
              </p>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div className="flex items-center gap-3">
          <h2 className="text-2xl font-bold">Validation des transactions</h2>
          <Badge variant="secondary" className="text-lg px-3 py-1">
            {totalPending} en attente
          </Badge>
        </div>
        <div className="flex gap-2">
          {uncategorizedGroups > 0 && (
            <Button
              variant="outline"
              onClick={categorizeAll}
              disabled={categorizingAll || aiLoading}
              className="border-purple-200 hover:bg-purple-50"
            >
              {categorizingAll ? (
                <>
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                  {categorizedCount}/{uncategorizedGroups}...
                </>
              ) : (
                <>
                  <Wand2 className="h-4 w-4 mr-2 text-purple-600" />
                  Catégoriser tout avec IA
                  {aiSettings.enabled && <Sparkles className="h-3 w-3 ml-1 text-amber-500" />}
                </>
              )}
            </Button>
          )}
          <Button
            variant="outline"
            onClick={handleIgnoreSelected}
            disabled={groups.every(g => g.ignoredIds.size === 0)}
          >
            <EyeOff className="h-4 w-4 mr-2" />
            Ignorer sélectionnés
          </Button>
          <Button
            onClick={handleValidateAll}
            disabled={!canValidateAll || validating}
            className="bg-emerald-600 hover:bg-emerald-700"
          >
            {validating ? (
              <>
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2" />
                Validation...
              </>
            ) : (
              <>
                <CheckCircle2 className="h-4 w-4 mr-2" />
                Valider tous ({groupsWithCategory} groupes)
              </>
            )}
          </Button>
        </div>
      </div>

      {/* Info alert */}
      <Alert>
        <AlertCircle className="h-4 w-4" />
        <AlertDescription className="flex items-center justify-between">
          <span>
            Les transactions sont regroupées par description similaire. 
            Sélectionnez une catégorie pour chaque groupe et validez-les en une seule fois.
          </span>
          {uncategorizedGroups > 0 && (
            <span className="text-sm text-gray-500">
              {uncategorizedGroups} groupe{uncategorizedGroups > 1 ? 's' : ''} sans catégorie
            </span>
          )}
        </AlertDescription>
      </Alert>

      {/* Groups list */}
      <div className="space-y-3">
        {groups.map((group) => {
          const isExpanded = expandedGroups.has(group.pattern);
          const activeCount = group.transactions.length - group.ignoredIds.size;
          const totalAmount = group.transactions
            .filter(tx => !group.ignoredIds.has(tx.id))
            .reduce((sum, tx) => sum + tx.amount, 0);
          const hasSuggestion = group.suggestedCategory && !group.selectedCategory;

          return (
            <Card key={group.pattern} className={group.ignoredIds.size === group.transactions.length ? 'opacity-50' : ''}>
              <CardContent className="p-4">
                {/* Header du groupe */}
                <div className="flex items-center gap-4">
                  <button
                    onClick={() => toggleGroup(group.pattern)}
                    className="p-1 hover:bg-gray-100 rounded"
                  >
                    {isExpanded ? (
                      <ChevronUp className="h-5 w-5 text-gray-500" />
                    ) : (
                      <ChevronDown className="h-5 w-5 text-gray-500" />
                    )}
                  </button>

                  <div className="flex-1">
                    <div className="flex items-center gap-2">
                      <h3 className="font-semibold text-lg">{group.pattern}</h3>
                      {group.suggestionSource && (
                        <Badge 
                          variant="outline" 
                          className="text-xs flex items-center gap-1"
                        >
                          {getSourceIcon(group.suggestionSource)}
                          {group.suggestionSource === 'ai' ? 'IA' : 
                           group.suggestionSource === 'rule' ? 'Règle' : 'Auto'}
                        </Badge>
                      )}
                    </div>
                    <p className="text-sm text-gray-500">
                      {activeCount} transaction{activeCount > 1 ? 's' : ''} • 
                      {' '}Total: {totalAmount.toFixed(2)} €
                      {group.ignoredIds.size > 0 && (
                        <span className="text-amber-600 ml-2">
                          ({group.ignoredIds.size} ignorée{group.ignoredIds.size > 1 ? 's' : ''})
                        </span>
                      )}
                    </p>
                  </div>

                  <div className="flex items-center gap-2">
                    {/* Suggestion badge */}
                    {hasSuggestion && (
                      <Badge 
                        variant="outline" 
                        className={`${getCategoryColor(group.suggestedCategory!)} cursor-pointer hover:opacity-80`}
                        onClick={() => handleCategoryChange(group.pattern, group.suggestedCategory!)}
                      >
                        Suggéré: {group.suggestedCategory}
                        {group.suggestionConfidence && (
                          <span className="ml-1 opacity-70">
                            ({Math.round(group.suggestionConfidence * 100)}%)
                          </span>
                        )}
                      </Badge>
                    )}

                    {/* Bouton IA pour ce groupe */}
                    {!group.selectedCategory && !hasSuggestion && (
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => categorizeGroup(group)}
                        disabled={aiLoading}
                        className="text-purple-600 hover:text-purple-700 hover:bg-purple-50"
                      >
                        {aiLoading ? (
                          <Loader2 className="h-4 w-4 animate-spin" />
                        ) : (
                          <>
                            <Sparkles className="h-4 w-4 mr-1" />
                            IA
                          </>
                        )}
                      </Button>
                    )}

                    <Select
                      value={group.selectedCategory}
                      onValueChange={(value) => handleCategoryChange(group.pattern, value)}
                    >
                      <SelectTrigger className="w-48">
                        <SelectValue placeholder="Choisir une catégorie..." />
                      </SelectTrigger>
                      <SelectContent>
                        {categories.map((cat) => (
                          <SelectItem key={cat.id} value={cat.name}>
                            <span className="flex items-center gap-2">
                              <span>{cat.emoji}</span>
                              <span>{cat.name}</span>
                            </span>
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>

                    <Button
                      size="sm"
                      onClick={() => handleValidateGroup(group)}
                      disabled={!group.selectedCategory || activeCount === 0 || validating}
                      className="bg-emerald-600 hover:bg-emerald-700"
                    >
                      <CheckCircle2 className="h-4 w-4 mr-1" />
                      Valider
                    </Button>
                  </div>
                </div>

                {/* Liste des transactions du groupe */}
                {isExpanded && (
                  <div className="mt-4 border-t pt-4">
                    <table className="w-full">
                      <thead>
                        <tr className="text-left text-sm text-gray-500">
                          <th className="pb-2 w-10"></th>
                          <th className="pb-2">Date</th>
                          <th className="pb-2">Description complète</th>
                          <th className="pb-2 text-right">Montant</th>
                        </tr>
                      </thead>
                      <tbody>
                        {group.transactions.map((tx) => (
                          <tr 
                            key={tx.id} 
                            className={group.ignoredIds.has(tx.id) ? 'opacity-50' : ''}
                          >
                            <td className="py-2">
                              <Checkbox
                                checked={group.ignoredIds.has(tx.id)}
                                onCheckedChange={() => toggleIgnoreTransaction(group.pattern, tx.id)}
                              />
                            </td>
                            <td className="py-2 text-sm">{tx.date}</td>
                            <td className="py-2">{tx.description}</td>
                            <td className={`py-2 text-right font-medium ${
                              tx.type === 'expense' ? 'text-red-600' : 'text-green-600'
                            }`}>
                              {tx.type === 'expense' ? '-' : '+'}{tx.amount.toFixed(2)} €
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}
              </CardContent>
            </Card>
          );
        })}
      </div>
    </div>
  );
}
