import { useQuery } from '@tanstack/react-query';
import { dashboardApi } from '@services/dashboard';

const QUERY_KEY = 'dashboard';

export const useDashboardStats = () => {
  return useQuery({
    queryKey: [QUERY_KEY, 'stats'],
    queryFn: () => dashboardApi.getStats(),
  });
};

export const useDashboardData = () => {
  return useQuery({
    queryKey: [QUERY_KEY, 'full'],
    queryFn: () => dashboardApi.getDashboardData(),
  });
};

export const useMonthlyTrend = (months: number = 12) => {
  return useQuery({
    queryKey: [QUERY_KEY, 'trend', months],
    queryFn: () => dashboardApi.getMonthlyTrend(months),
  });
};

export const useSpendingByCategory = (startDate?: string, endDate?: string) => {
  return useQuery({
    queryKey: [QUERY_KEY, 'spending', startDate, endDate],
    queryFn: () => dashboardApi.getSpendingByCategory(startDate, endDate),
  });
};
