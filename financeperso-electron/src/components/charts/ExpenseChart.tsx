import * as React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import {
  PieChart,
  Pie,
  Cell,
  ResponsiveContainer,
  Tooltip,
  Legend,
} from 'recharts';
import type { CategoryStat } from '@/types';

interface ExpenseChartProps {
  data: CategoryStat[];
}

// Palette de couleurs dynamiques pour les catégories
const COLORS = [
  '#10b981', // emerald-500
  '#3b82f6', // blue-500
  '#f59e0b', // amber-500
  '#ef4444', // red-500
  '#8b5cf6', // violet-500
  '#ec4899', // pink-500
  '#06b6d4', // cyan-500
  '#84cc16', // lime-500
  '#f97316', // orange-500
  '#6366f1', // indigo-500
  '#14b8a6', // teal-500
  '#a855f7', // purple-500
];

interface TooltipProps {
  active?: boolean;
  payload?: Array<{
    name: string;
    value: number;
    payload: CategoryStat;
  }>;
}

const CustomTooltip = ({ active, payload }: TooltipProps) => {
  if (active && payload && payload.length) {
    const data = payload[0].payload;
    const total = payload[0].payload.total || 1;
    const percentage = ((data.total / total) * 100).toFixed(1);
    
    return (
      <div className="bg-white p-3 rounded-lg shadow-lg border border-gray-200">
        <p className="font-semibold text-gray-900">{data.category}</p>
        <p className="text-sm text-gray-600">
          Montant: <span className="font-medium">{data.total.toFixed(2)}€</span>
        </p>
        <p className="text-sm text-gray-600">
          Pourcentage: <span className="font-medium">{percentage}%</span>
        </p>
        <p className="text-sm text-gray-600">
          Transactions: <span className="font-medium">{data.count}</span>
        </p>
      </div>
    );
  }
  return null;
};

export function ExpenseChart({ data }: ExpenseChartProps) {
  // Filtrer uniquement les dépenses (montants positifs dans categoryStats)
  const chartData = data
    .filter(item => item.total > 0)
    .sort((a, b) => b.total - a.total)
    .slice(0, 8); // Limiter à 8 catégories pour la lisibilité

  // Calculer le total pour les pourcentages
  const total = chartData.reduce((sum, item) => sum + item.total, 0);
  
  // Ajouter le total à chaque item pour le tooltip
  const enrichedData = chartData.map(item => ({
    ...item,
    total,
  }));

  if (chartData.length === 0) {
    return (
      <Card className="h-full">
        <CardHeader>
          <CardTitle className="text-lg">Répartition des dépenses</CardTitle>
        </CardHeader>
        <CardContent className="flex items-center justify-center h-64">
          <p className="text-muted-foreground text-center">
            Aucune dépense ce mois-ci
          </p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="h-full">
      <CardHeader>
        <CardTitle className="text-lg">Répartition des dépenses</CardTitle>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={280}>
          <PieChart>
            <Pie
              data={enrichedData}
              cx="50%"
              cy="50%"
              innerRadius={60}
              outerRadius={100}
              paddingAngle={2}
              dataKey="total"
              nameKey="category"
            >
              {enrichedData.map((entry, index) => (
                <Cell 
                  key={`cell-${index}`} 
                  fill={COLORS[index % COLORS.length]} 
                />
              ))}
            </Pie>
            <Tooltip content={<CustomTooltip />} />
            <Legend 
              verticalAlign="bottom" 
              height={36}
              formatter={(value: string, entry: any) => (
                <span className="text-sm text-gray-700">{value}</span>
              )}
            />
          </PieChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
}
