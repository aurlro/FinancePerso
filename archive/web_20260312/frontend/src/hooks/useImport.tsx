/**
 * @file useImport.tsx
 * @description Hook pour l'import de transactions CSV - VERSION API FASTAPI
 * 
 * Endpoints utilisés:
 * - POST /api/transactions/import
 */

import { useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { importApi, type CsvMapping, type ImportResponse } from "@/lib/api";

export interface ImportOptions {
  accountId: number;
  csvContent: string;
  mapping: CsvMapping;
  skipDuplicates?: boolean;
}

export function useImportTransactions() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async (options: ImportOptions): Promise<ImportResponse> => {
      const response = await importApi.importCsv(
        options.accountId,
        options.csvContent,
        options.mapping,
        options.skipDuplicates ?? true
      );
      return response;
    },
    onSuccess: (data) => {
      // Invalidate transactions query to refresh the list
      queryClient.invalidateQueries({ queryKey: ["transactions"] });
      
      // Show summary toast
      const messages = [];
      if (data.imported > 0) messages.push(`${data.imported} importée(s)`);
      if (data.duplicates > 0) messages.push(`${data.duplicates} doublon(s) ignoré(s)`);
      if (data.errors > 0) messages.push(`${data.errors} erreur(s)`);
      
      if (messages.length > 0) {
        toast.success(`Import terminé: ${messages.join(", ")}`);
      }
      
      if (data.transfer_detected_count > 0) {
        toast.info(`${data.transfer_detected_count} virement(s) interne(s) détecté(s)`);
      }
      
      if (data.attributed_count > 0) {
        toast.info(`${data.attributed_count} transaction(s) attribuée(s) automatiquement`);
      }
    },
    onError: (e: Error) => {
      toast.error(e.message || "Erreur lors de l'import");
    },
  });
}
