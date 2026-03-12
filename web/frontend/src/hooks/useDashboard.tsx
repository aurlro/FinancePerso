/**
 * @file useDashboard.tsx
 * @description Hook pour les données du dashboard - VERSION ADAPTÉE POUR FASTAPI
 * 
 * ⚠️  À ADAPTER : Remplacer les appels Supabase par des appels à l'API FastAPI
 */

import { useQuery } from "@tanstack/react-query";

// TODO: Déplacer dans types/dashboard.ts
export interface DashboardMetrics {
  totalBalance: number;
  monthlyIncome: number;
  monthlyExpenses: number;
  savingsRate: number;
  transactionsCount: number;
  alerts: Alert[];
}

export interface Alert {
  id: string;
  type: "warning" | "info" | "success" | "error";
  title: string;
  message: string;
  date: string;
}

export interface MonthlyData {
  month: string;
  income: number;
  expenses: number;
  savings: number;
}

export interface CategoryBreakdown {
  category: string;
  amount: number;
  percentage: number;
  color: string;
}

// ============================================
// MOCK DATA - À REMPLACER PAR API FASTAPI
// ============================================
const MOCK_METRICS: DashboardMetrics = {
  totalBalance: 12540.5,
  monthlyIncome: 4500.0,
  monthlyExpenses: 3200.75,
  savingsRate: 28.9,
  transactionsCount: 42,
  alerts: [
    {
      id: "1",
      type: "warning",
      title: "Budget Alimentation",
      message: "Vous avez atteint 85% de votre budget",
      date: new Date().toISOString(),
    },
  ],
};

const MOCK_MONTHLY_DATA: MonthlyData[] = [
  { month: "Jan", income: 4200, expenses: 3100, savings: 1100 },
  { month: "Fév", income: 4200, expenses: 2900, savings: 1300 },
  { month: "Mar", income: 4500, expenses: 3200, savings: 1300 },
];

const MOCK_CATEGORY_DATA: CategoryBreakdown[] = [
  { category: "Alimentation", amount: 450, percentage: 25, color: "#22c55e" },
  { category: "Transport", amount: 320, percentage: 18, color: "#3b82f6" },
  { category: "Logement", amount: 800, percentage: 44, color: "#f59e0b" },
  { category: "Loisirs", amount: 230, percentage: 13, color: "#ef4444" },
];

// ============================================
// API CLIENT - Configuration de base
// ============================================
const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000/api";

async function fetchApi<T>(endpoint: string): Promise<T> {
  const token = localStorage.getItem("fp_token");
  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    headers: {
      "Content-Type": "application/json",
      ...(token && { Authorization: `Bearer ${token}` }),
    },
  });
  
  if (!response.ok) {
    throw new Error(`API Error: ${response.status}`);
  }
  
  return response.json();
}

// ============================================
// HOOKS REACT QUERY
// ============================================

export function useDashboardMetrics() {
  return useQuery({
    queryKey: ["dashboard", "metrics"],
    queryFn: async (): Promise<DashboardMetrics> => {
      // TODO: Remplacer par : GET /api/dashboard/metrics
      // return fetchApi<DashboardMetrics>("/dashboard/metrics");
      
      // Mock pour le développement
      await new Promise(resolve => setTimeout(resolve, 300));
      return MOCK_METRICS;
    },
  });
}

export function useMonthlyTrends() {
  return useQuery({
    queryKey: ["dashboard", "monthly-trends"],
    queryFn: async (): Promise<MonthlyData[]> => {
      // TODO: Remplacer par : GET /api/dashboard/monthly-trends
      await new Promise(resolve => setTimeout(resolve, 300));
      return MOCK_MONTHLY_DATA;
    },
  });
}

export function useCategoryBreakdown() {
  return useQuery({
    queryKey: ["dashboard", "category-breakdown"],
    queryFn: async (): Promise<CategoryBreakdown[]> => {
      // TODO: Remplacer par : GET /api/dashboard/categories
      await new Promise(resolve => setTimeout(resolve, 300));
      return MOCK_CATEGORY_DATA;
    },
  });
}
