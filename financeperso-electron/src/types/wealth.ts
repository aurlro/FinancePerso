// Types pour le module Patrimoine

export type WealthAccountType = 'checking' | 'savings' | 'investment' | 'crypto' | 'other';

export interface WealthAccount {
  id: number;
  name: string;
  type: WealthAccountType;
  balance: number;
  currency: string;
  institution?: string;
  is_active: number;
  created_at?: string;
}

export interface SavingsGoal {
  id: number;
  name: string;
  target_amount: number;
  current_amount: number;
  deadline?: string;
  category?: string;
  monthly_contribution?: number;
  is_active: number;
  created_at?: string;
}

export interface ProjectionData {
  month: number;
  year: number;
  amount: number;
  contributions: number;
  interest: number;
}

export interface ProjectionResult {
  finalAmount: number;
  totalContributions: number;
  totalInterest: number;
  monthlyData: ProjectionData[];
}

export interface WealthStats {
  totalWealth: number;
  totalChecking: number;
  totalSavings: number;
  totalInvestments: number;
  totalCrypto: number;
  monthlyChange: number;
  yearlyChange: number;
}

export interface WealthDistribution {
  type: WealthAccountType;
  amount: number;
  percentage: number;
  color: string;
}

// Configuration pour le simulateur
export interface SimulatorConfig {
  initialAmount: number;
  monthlyContribution: number;
  annualRate: number;
  years: number;
}
