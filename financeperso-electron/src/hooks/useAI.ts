import { useState, useCallback, useEffect } from 'react';
import { useIPC } from './useIPC';

export interface CategorizationResult {
  category: string;
  confidence: number;
  source: 'ai' | 'fallback' | 'fallback_error' | 'rule';
}

export interface AISettings {
  provider: 'gemini' | 'openai' | 'local';
  apiKey: string;
  model: string;
  enabled: boolean;
  autoCategorize: boolean;
}

export interface LearningRule {
  id: number;
  pattern: string;
  category: string;
  confidence: number;
  usage_count: number;
  source: string;
  created_at: string;
  updated_at: string;
}

export function useAI() {
  const { categorizeWithAI, getAISettings, saveAISettings, testAIConnection, getLearningRules, createLearningRule } = useIPC();
  
  const [settings, setSettings] = useState<AISettings>({
    provider: 'gemini',
    apiKey: '',
    model: 'gemini-2.0-flash',
    enabled: false,
    autoCategorize: false,
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [testing, setTesting] = useState(false);
  const [testResult, setTestResult] = useState<{ success: boolean; message: string } | null>(null);

  // Charger les paramètres au montage
  useEffect(() => {
    loadSettings();
  }, []);

  const loadSettings = useCallback(async () => {
    try {
      const savedSettings = await getAISettings();
      if (savedSettings) {
        setSettings(savedSettings);
      }
    } catch (err) {
      console.error('Failed to load AI settings:', err);
    }
  }, [getAISettings]);

  /**
   * Catégorise une transaction avec l'IA
   */
  const categorize = useCallback(async (
    label: string, 
    amount: number = 0
  ): Promise<CategorizationResult | null> => {
    try {
      setLoading(true);
      setError(null);
      const result = await categorizeWithAI(label, amount);
      return result;
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Erreur de catégorisation';
      setError(message);
      return null;
    } finally {
      setLoading(false);
    }
  }, [categorizeWithAI]);

  /**
   * Catégorise plusieurs transactions en batch
   */
  const categorizeBatch = useCallback(async (
    transactions: Array<{ label: string; amount: number }>
  ): Promise<CategorizationResult[]> => {
    try {
      setLoading(true);
      setError(null);
      
      const results: CategorizationResult[] = [];
      
      // Traiter par petits groupes pour éviter de bloquer l'UI
      for (const tx of transactions) {
        const result = await categorizeWithAI(tx.label, tx.amount);
        if (result) {
          results.push(result);
        }
      }
      
      return results;
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Erreur de catégorisation batch';
      setError(message);
      return [];
    } finally {
      setLoading(false);
    }
  }, [categorizeWithAI]);

  /**
   * Récupère des suggestions de catégories pour un libellé
   */
  const getSuggestions = useCallback(async (
    label: string,
    maxSuggestions: number = 3
  ): Promise<Array<{ category: string; confidence: number; source: string }>> => {
    try {
      // D'abord, chercher dans les règles d'apprentissage
      const rules = await getLearningRules();
      const matchingRules = rules
        .filter((rule: LearningRule) => 
          label.toUpperCase().includes(rule.pattern) || 
          rule.pattern.includes(label.toUpperCase())
        )
        .sort((a: LearningRule, b: LearningRule) => b.confidence - a.confidence)
        .slice(0, maxSuggestions)
        .map((rule: LearningRule) => ({
          category: rule.category,
          confidence: rule.confidence,
          source: 'rule'
        }));

      if (matchingRules.length > 0) {
        return matchingRules;
      }

      // Si pas de règle, utiliser l'IA
      const result = await categorize(label, 0);
      if (result) {
        return [{
          category: result.category,
          confidence: result.confidence,
          source: result.source
        }];
      }

      return [];
    } catch (err) {
      console.error('Failed to get suggestions:', err);
      return [];
    }
  }, [getLearningRules, categorize]);

  /**
   * Teste la connexion à l'API IA
   */
  const testConnection = useCallback(async (): Promise<boolean> => {
    try {
      setTesting(true);
      setTestResult(null);
      const result = await testAIConnection();
      setTestResult(result);
      return result.success;
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Erreur de test';
      setTestResult({ success: false, message });
      return false;
    } finally {
      setTesting(false);
    }
  }, [testAIConnection]);

  /**
   * Sauvegarde les paramètres IA
   */
  const saveSettings = useCallback(async (newSettings: Partial<AISettings>): Promise<boolean> => {
    try {
      setLoading(true);
      const updatedSettings = { ...settings, ...newSettings };
      await saveAISettings(updatedSettings);
      setSettings(updatedSettings);
      return true;
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Erreur de sauvegarde';
      setError(message);
      return false;
    } finally {
      setLoading(false);
    }
  }, [settings, saveAISettings]);

  /**
   * Crée une nouvelle règle d'apprentissage
   */
  const createRule = useCallback(async (
    pattern: string, 
    category: string,
    confidence: number = 1.0
  ): Promise<boolean> => {
    try {
      await createLearningRule(pattern, category, confidence);
      return true;
    } catch (err) {
      console.error('Failed to create rule:', err);
      return false;
    }
  }, [createLearningRule]);

  return {
    // État
    settings,
    loading,
    error,
    testing,
    testResult,
    
    // Méthodes
    categorize,
    categorizeBatch,
    getSuggestions,
    testConnection,
    saveSettings,
    createRule,
    refreshSettings: loadSettings,
    clearError: () => setError(null),
    clearTestResult: () => setTestResult(null),
  };
}

/**
 * Hook spécialisé pour la catégorisation IA des transactions
 */
export function useAICategorization() {
  const ai = useAI();
  const [results, setResults] = useState<Map<string, CategorizationResult>>(new Map());

  /**
   * Catégorise une transaction et stocke le résultat
   */
  const categorizeTransaction = useCallback(async (
    transactionId: string,
    label: string,
    amount: number
  ): Promise<CategorizationResult | null> => {
    const result = await ai.categorize(label, amount);
    if (result) {
      setResults(prev => new Map(prev).set(transactionId, result));
    }
    return result;
  }, [ai]);

  /**
   * Récupère le résultat de catégorisation pour une transaction
   */
  const getResult = useCallback((transactionId: string): CategorizationResult | undefined => {
    return results.get(transactionId);
  }, [results]);

  /**
   * Applique une catégorisation suggérée
   */
  const applySuggestion = useCallback((transactionId: string, category: string): boolean => {
    const result = results.get(transactionId);
    if (result) {
      setResults(prev => new Map(prev).set(transactionId, {
        ...result,
        category,
        confidence: 1.0,
        source: 'manual'
      }));
      return true;
    }
    return false;
  }, [results]);

  /**
   * Efface tous les résultats
   */
  const clearResults = useCallback(() => {
    setResults(new Map());
  }, []);

  return {
    ...ai,
    results,
    categorizeTransaction,
    getResult,
    applySuggestion,
    clearResults,
  };
}
