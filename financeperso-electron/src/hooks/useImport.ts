import { useState, useCallback } from 'react';
import { useIPC } from './useIPC';
import type { ImportResult, ImportOptions } from '../types';

interface ImportState {
  isImporting: boolean;
  result: ImportResult | null;
  error: string | null;
}

export function useImport() {
  const [state, setState] = useState<ImportState>({
    isImporting: false,
    result: null,
    error: null,
  });

  const { selectCSV, importCSV } = useIPC();

  const importFile = useCallback(async (options?: ImportOptions) => {
    try {
      setState({ isImporting: true, result: null, error: null });

      // Ouvrir le dialogue de sélection
      const filePath = await selectCSV();
      
      if (!filePath) {
        // Utilisateur a annulé
        setState({ isImporting: false, result: null, error: null });
        return null;
      }

      // Importer le fichier
      const result = await importCSV(filePath, options);

      if (result.success) {
        setState({ isImporting: false, result, error: null });
      } else {
        setState({ 
          isImporting: false, 
          result, 
          error: result.error || 'Erreur lors de l\'import' 
        });
      }

      return result;
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Erreur inconnue';
      setState({ isImporting: false, result: null, error: errorMsg });
      return null;
    }
  }, [selectCSV, importCSV]);

  const reset = useCallback(() => {
    setState({ isImporting: false, result: null, error: null });
  }, []);

  return {
    ...state,
    importFile,
    reset,
  };
}
