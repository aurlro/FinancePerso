import api from './api';
import type {
  DashboardStats,
  DashboardData,
  MonthlyTrend,
  CashflowForecast,
  SpendingByCategory,
} from '@types';

const BASE_URL = '/dashboard';

export const dashboardApi = {
  // Get main dashboard stats
  getStats: async (): Promise<DashboardStats> => {
    const response = await api.get(`${BASE_URL}/stats`);
    return response.data.data;
  },

  // Get full dashboard data
  getDashboardData: async (): Promise<DashboardData> => {
    const response = await api.get(BASE_URL);
    return response.data.data;
  },

  // Get monthly trend
  getMonthlyTrend: async (months: number = 12): Promise<MonthlyTrend[]> => {
    const response = await api.get(`${BASE_URL}/trend`, { params: { months } });
    return response.data.data;
  },

  // Get spending by category
  getSpendingByCategory: async (
    startDate?: string,
    endDate?: string
  ): Promise<SpendingByCategory[]> => {
    const response = await api.get(`${BASE_URL}/spending`, {
      params: { start_date: startDate, end_date: endDate },
    });
    return response.data.data;
  },

  // Get cashflow forecast
  getForecast: async (months: number = 6): Promise<CashflowForecast[]> => {
    const response = await api.get(`${BASE_URL}/forecast`, { params: { months } });
    return response.data.data;
  },
};
