/**
 * Hooks React Query pour l'Export (PR #8)
 * Export CSV, JSON, et rapports
 */

import { useQuery, useMutation } from "@tanstack/react-query";
import { exportApi } from "@/lib/api";

// Hook pour exporter les transactions en CSV
export function useExportTransactionsCsv() {
  return useMutation({
    mutationFn: (params: {
      startDate?: string;
      endDate?: string;
      category?: string;
      status?: string;
    }) => exportApi.exportCsv(params),
  });
}

// Hook pour exporter les transactions en JSON
export function useExportTransactionsJson() {
  return useQuery({
    queryKey: ["export", "transactions", "json"],
    queryFn: () => exportApi.exportJson({}),
    enabled: false, // Manuel uniquement
  });
}

// Hook pour obtenir le rapport mensuel
export function useMonthlyReport(month: string | null) {
  return useQuery({
    queryKey: ["export", "report", "monthly", month],
    queryFn: () => exportApi.getMonthlyReport(month!),
    enabled: !!month,
    staleTime: 5 * 60 * 1000,
  });
}

// Hook pour obtenir le rapport annuel
export function useAnnualReport(year: number | null) {
  return useQuery({
    queryKey: ["export", "report", "annual", year],
    queryFn: () => exportApi.getAnnualReport(year!),
    enabled: !!year,
    staleTime: 5 * 60 * 1000,
  });
}

// Hook pour créer une sauvegarde complète
export function useFullBackup() {
  return useQuery({
    queryKey: ["export", "backup"],
    queryFn: () => exportApi.getFullBackup(),
    enabled: false, // Manuel uniquement
  });
}

// Fonction utilitaire pour télécharger un fichier
export function downloadFile(content: Blob | string, filename: string, contentType: string) {
  const blob = content instanceof Blob ? content : new Blob([content], { type: contentType });
  const url = window.URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  window.URL.revokeObjectURL(url);
}
