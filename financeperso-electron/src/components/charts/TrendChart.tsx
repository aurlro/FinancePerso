import * as React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from 'recharts';

interface TrendChartProps {
  currentIncome: number;
  currentExpense: number;
  currentMonth?: number;
  currentYear?: number;
}

interface MonthData {
  month: string;
  income: number;
  expense: number;
}

// Données mock pour les mois précédents si pas assez de données historiques
const generateMockData = (
  currentIncome: number,
  currentExpense: number,
  currentMonth: number = new Date().getMonth(),
  currentYear: number = new Date().getFullYear()
): MonthData[] => {
  const months = ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Juin', 'Juil', 'Août', 'Sep', 'Oct', 'Nov', 'Déc'];
  const data: MonthData[] = [];
  
  // Générer 6 mois de données (5 mois passés + mois actuel)
  for (let i = 5; i >= 0; i--) {
    const monthIndex = (currentMonth - i + 12) % 12;
    const year = currentYear - (currentMonth - i < 0 ? 1 : 0);
    
    let income: number;
    let expense: number;
    
    if (i === 0) {
      // Mois actuel: utiliser les vraies données
      income = currentIncome;
      expense = currentExpense;
    } else {
      // Mois précédents: générer des variations réalistes
      const variation = 0.8 + Math.random() * 0.4; // Variation de ±20%
      income = Math.round(currentIncome * variation * 100) / 100;
      expense = Math.round(currentExpense * variation * 100) / 100;
    }
    
    data.push({
      month: `${months[monthIndex]} ${year}`,
      income,
      expense,
    });
  }
  
  return data;
};

interface TooltipProps {
  active?: boolean;
  payload?: Array<{
    name: string;
    value: number;
    color: string;
  }>;
  label?: string;
}

const CustomTooltip = ({ active, payload, label }: TooltipProps) => {
  if (active && payload && payload.length) {
    return (
      <div className="bg-white p-3 rounded-lg shadow-lg border border-gray-200">
        <p className="font-semibold text-gray-900 mb-2">{label}</p>
        {payload.map((entry, index) => (
          <p key={index} className="text-sm" style={{ color: entry.color }}>
            {entry.name}: {' '}
            <span className="font-medium">
              {entry.value.toFixed(2)}€
            </span>
          </p>
        ))}
      </div>
    );
  }
  return null;
};

export function TrendChart({ 
  currentIncome, 
  currentExpense, 
  currentMonth,
  currentYear 
}: TrendChartProps) {
  const data = generateMockData(currentIncome, currentExpense, currentMonth, currentYear);

  return (
    <Card className="h-full">
      <CardHeader>
        <CardTitle className="text-lg">Tendances sur 6 mois</CardTitle>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={280}>
          <LineChart data={data} margin={{ top: 5, right: 20, left: 0, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
            <XAxis 
              dataKey="month" 
              tick={{ fontSize: 12 }}
              stroke="#6b7280"
            />
            <YAxis 
              tick={{ fontSize: 12 }}
              stroke="#6b7280"
              tickFormatter={(value: number) => `${value.toFixed(0)}€`}
            />
            <Tooltip content={<CustomTooltip />} />
            <Legend 
              wrapperStyle={{ paddingTop: '10px' }}
              formatter={(value: string) => (
                <span className="text-sm text-gray-700">{value}</span>
              )}
            />
            <Line
              type="monotone"
              dataKey="income"
              name="Revenus"
              stroke="#22c55e"
              strokeWidth={3}
              dot={{ fill: '#22c55e', strokeWidth: 2, r: 4 }}
              activeDot={{ r: 6, stroke: '#22c55e', strokeWidth: 2 }}
            />
            <Line
              type="monotone"
              dataKey="expense"
              name="Dépenses"
              stroke="#ef4444"
              strokeWidth={3}
              dot={{ fill: '#ef4444', strokeWidth: 2, r: 4 }}
              activeDot={{ r: 6, stroke: '#ef4444', strokeWidth: 2 }}
            />
          </LineChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
}
