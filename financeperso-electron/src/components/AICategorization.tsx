import * as React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Sparkles, CheckCircle2, XCircle, Loader2, Brain, Zap, AlertTriangle } from 'lucide-react';
import { useAICategorization, type CategorizationResult } from '@/hooks/useAI';
import type { Transaction } from '@/types';

interface AICategorizationProps {
  transaction: Transaction;
  onApply?: (category: string) => void;
  onDismiss?: () => void;
  autoCategorize?: boolean;
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
 * Retourne l'icône associée à la source de catégorisation
 */
function getSourceIcon(source: string) {
  switch (source) {
    case 'ai':
      return <Brain className="h-3 w-3" />;
    case 'rule':
      return <Zap className="h-3 w-3" />;
    case 'fallback':
      return <AlertTriangle className="h-3 w-3" />;
    default:
      return null;
  }
}

/**
 * Retourne le label associé à la source de catégorisation
 */
function getSourceLabel(source: string): string {
  switch (source) {
    case 'ai':
      return 'IA';
    case 'rule':
      return 'Règle';
    case 'fallback':
      return 'Auto';
    case 'fallback_error':
      return 'Fallback';
    default:
      return source;
  }
}

/**
 * Formate le score de confiance en pourcentage
 */
function formatConfidence(confidence: number): string {
  return `${Math.round(confidence * 100)}%`;
}

/**
 * Détermine la couleur du score de confiance
 */
function getConfidenceColor(confidence: number): string {
  if (confidence >= 0.8) return 'text-green-600';
  if (confidence >= 0.6) return 'text-yellow-600';
  return 'text-orange-600';
}

export function AICategorization({ 
  transaction, 
  onApply, 
  onDismiss,
  autoCategorize = false 
}: AICategorizationProps) {
  const { 
    categorizeTransaction, 
    getResult, 
    loading, 
    error, 
    clearError 
  } = useAICategorization();
  
  const [result, setResult] = React.useState<CategorizationResult | null>(null);
  const [applied, setApplied] = React.useState(false);

  const transactionId = transaction.id.toString();

  // Catégorisation automatique au montage si activée
  React.useEffect(() => {
    if (autoCategorize && !transaction.category && !result && !loading) {
      handleCategorize();
    }
  }, [autoCategorize, transaction.id]);

  // Met à jour le résultat depuis le cache
  React.useEffect(() => {
    const cached = getResult(transactionId);
    if (cached) {
      setResult(cached);
    }
  }, [transactionId, getResult]);

  const handleCategorize = async () => {
    clearError();
    const categorization = await categorizeTransaction(
      transactionId,
      transaction.description,
      transaction.amount
    );
    if (categorization) {
      setResult(categorization);
    }
  };

  const handleApply = () => {
    if (result && onApply) {
      onApply(result.category);
      setApplied(true);
    }
  };

  const handleDismiss = () => {
    if (onDismiss) {
      onDismiss();
    }
  };

  // Affiche l'état de chargement
  if (loading && !result) {
    return (
      <Card className="border-dashed border-2 border-gray-200">
        <CardContent className="p-4">
          <div className="flex items-center gap-3">
            <Loader2 className="h-5 w-5 animate-spin text-emerald-600" />
            <div className="flex-1">
              <p className="text-sm font-medium text-gray-700">
                Analyse par IA en cours...
              </p>
              <p className="text-xs text-gray-500">
                "{transaction.description.slice(0, 40)}..."
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    );
  }

  // Affiche une erreur
  if (error && !result) {
    return (
      <Alert variant="destructive" className="text-sm">
        <AlertTriangle className="h-4 w-4" />
        <AlertDescription className="flex items-center justify-between">
          <span>{error}</span>
          <Button 
            variant="ghost" 
            size="sm" 
            onClick={handleCategorize}
            className="h-6 text-xs"
          >
            Réessayer
          </Button>
        </AlertDescription>
      </Alert>
    );
  }

  // Affiche le résultat de catégorisation
  if (result) {
    return (
      <Card className={`border-2 transition-all ${
        applied 
          ? 'border-green-200 bg-green-50/50' 
          : 'border-emerald-200 bg-emerald-50/30'
      }`}>
        <CardContent className="p-3">
          <div className="flex items-center gap-3">
            {/* Icône IA */}
            <div className={`p-2 rounded-full ${
              applied ? 'bg-green-100' : 'bg-emerald-100'
            }`}>
              {applied ? (
                <CheckCircle2 className="h-4 w-4 text-green-600" />
              ) : (
                <Sparkles className="h-4 w-4 text-emerald-600" />
              )}
            </div>

            {/* Résultat */}
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2 flex-wrap">
                <Badge 
                  variant="outline" 
                  className={`${getCategoryColor(result.category)} font-medium`}
                >
                  {result.category}
                </Badge>
                
                <Badge 
                  variant="secondary" 
                  className="text-xs flex items-center gap-1"
                >
                  {getSourceIcon(result.source)}
                  {getSourceLabel(result.source)}
                </Badge>

                {!applied && (
                  <span className={`text-xs font-medium ${getConfidenceColor(result.confidence)}`}>
                    {formatConfidence(result.confidence)}
                  </span>
                )}
              </div>

              {applied && (
                <p className="text-xs text-green-600 mt-1">
                  Catégorie appliquée
                </p>
              )}
            </div>

            {/* Actions */}
            {!applied && (
              <div className="flex items-center gap-1">
                <Button
                  size="sm"
                  onClick={handleApply}
                  className="h-7 px-2 bg-emerald-600 hover:bg-emerald-700"
                >
                  <CheckCircle2 className="h-3 w-3 mr-1" />
                  Appliquer
                </Button>
                {onDismiss && (
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={handleDismiss}
                    className="h-7 px-2 text-gray-400 hover:text-gray-600"
                  >
                    <XCircle className="h-3 w-3" />
                  </Button>
                )}
              </div>
            )}
          </div>
        </CardContent>
      </Card>
    );
  }

  // État initial - bouton pour catégoriser
  return (
    <Card className="border-dashed border-2 border-gray-200 hover:border-emerald-300 transition-colors cursor-pointer"
          onClick={handleCategorize}>
      <CardContent className="p-3">
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-full bg-gray-100">
            <Sparkles className="h-4 w-4 text-gray-400" />
          </div>
          <div className="flex-1">
            <p className="text-sm font-medium text-gray-600">
              Catégoriser avec l'IA
            </p>
            <p className="text-xs text-gray-400">
              Cliquez pour analyser cette transaction
            </p>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

/**
 * Composant pour afficher une liste de suggestions de catégories
 */
interface AICategorySuggestionsProps {
  label: string;
  onSelect: (category: string) => void;
  maxSuggestions?: number;
}

export function AICategorySuggestions({ 
  label, 
  onSelect, 
  maxSuggestions = 3 
}: AICategorySuggestionsProps) {
  const { getSuggestions, loading } = useAICategorization();
  const [suggestions, setSuggestions] = React.useState<Array<{
    category: string;
    confidence: number;
    source: string;
  }>>([]);

  React.useEffect(() => {
    const loadSuggestions = async () => {
      const results = await getSuggestions(label, maxSuggestions);
      setSuggestions(results);
    };
    
    if (label) {
      loadSuggestions();
    }
  }, [label]);

  if (loading || suggestions.length === 0) {
    return null;
  }

  return (
    <div className="flex items-center gap-2 flex-wrap mt-2">
      <span className="text-xs text-gray-400">Suggestions:</span>
      {suggestions.map((suggestion, index) => (
        <button
          key={`${suggestion.category}-${index}`}
          onClick={() => onSelect(suggestion.category)}
          className={`inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium 
            transition-all hover:scale-105 ${getCategoryColor(suggestion.category)}`}
        >
          {suggestion.category}
          <span className="opacity-60">
            {formatConfidence(suggestion.confidence)}
          </span>
        </button>
      ))}
    </div>
  );
}

export default AICategorization;
