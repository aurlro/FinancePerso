import * as React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { useWealthAccounts } from '@/hooks/useWealth';
import { 
  PieChart, 
  Pie, 
  Cell, 
  ResponsiveContainer,
  Tooltip,
  Legend
} from 'recharts';

// Format currency
const formatCurrency = (amount: number) => {
  return new Intl.NumberFormat('fr-FR', {
    style: 'currency',
    currency: 'EUR',
    maximumFractionDigits: 0,
  }).format(amount);
};

// Labels pour les types de comptes
const typeLabels: Record<string, string> = {
  checking: 'Liquidités',
  savings: 'Épargne',
  investment: 'Investissements',
  crypto: 'Crypto',
  other: 'Autre',
};

// Icons pour les types
const typeIcons: Record<string, string> = {
  checking: '💰',
  savings: '🏦',
  investment: '📈',
  crypto: '₿',
  other: '📦',
};

interface AccountItemProps {
  type: string;
  amount: number;
  percentage: number;
  color: string;
}

function AccountItem({ type, amount, percentage, color }: AccountItemProps) {
  return (
    <div className="flex items-center justify-between py-3 border-b last:border-0">
      <div className="flex items-center gap-3">
        <div 
          className="w-3 h-3 rounded-full"
          style={{ backgroundColor: color }}
        />
        <span className="text-lg">{typeIcons[type]}</span>
        <span className="font-medium">{typeLabels[type]}</span>
      </div>
      <div className="text-right">
        <p className="font-semibold">{formatCurrency(amount)}</p>
        <p className="text-sm text-gray-500">{percentage.toFixed(1)}%</p>
      </div>
    </div>
  );
}

export function WealthDistribution() {
  const { distribution, accounts, stats } = useWealthAccounts();

  // Données pour le pie chart
  const chartData = distribution.map(d => ({
    name: typeLabels[d.type],
    value: d.amount,
    color: d.color,
  }));

  // Grouper les comptes par type
  const accountsByType = React.useMemo(() => {
    const grouped: Record<string, typeof accounts> = {};
    accounts.forEach(account => {
      if (!grouped[account.type]) {
        grouped[account.type] = [];
      }
      grouped[account.type].push(account);
    });
    return grouped;
  }, [accounts]);

  if (distribution.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Répartition du patrimoine</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-gray-500 text-center py-8">
            Aucun compte configuré. Ajoutez des comptes pour voir la répartition.
          </p>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      {/* Graphique et liste côte à côte */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Pie Chart */}
        <Card>
          <CardHeader>
            <CardTitle>Répartition visuelle</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-[300px]">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={chartData}
                    cx="50%"
                    cy="50%"
                    innerRadius={60}
                    outerRadius={100}
                    paddingAngle={2}
                    dataKey="value"
                  >
                    {chartData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip formatter={(value: number) => formatCurrency(value)} />
                  <Legend />
                </PieChart>
              </ResponsiveContainer>
            </div>
            
            {/* Total au centre */}
            <div className="text-center -mt-32 mb-8 relative z-10 pointer-events-none">
              <p className="text-sm text-gray-500">Total</p>
              <p className="text-2xl font-bold">{formatCurrency(stats.totalWealth)}</p>
            </div>
          </CardContent>
        </Card>

        {/* Liste par type */}
        <Card>
          <CardHeader>
            <CardTitle>Répartition par type</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-1">
              {distribution.map((item) => (
                <AccountItem
                  key={item.type}
                  type={item.type}
                  amount={item.amount}
                  percentage={item.percentage}
                  color={item.color}
                />
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Détails des comptes */}
      <Card>
        <CardHeader>
          <CardTitle>Détail des comptes</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-6">
            {Object.entries(accountsByType).map(([type, typeAccounts]) => (
              <div key={type}>
                <h4 className="text-sm font-semibold text-gray-500 uppercase tracking-wide mb-3 flex items-center gap-2">
                  <span>{typeIcons[type]}</span>
                  {typeLabels[type]}
                </h4>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                  {typeAccounts.map(account => (
                    <div 
                      key={account.id}
                      className="p-4 rounded-lg border bg-gray-50 hover:bg-gray-100 transition-colors"
                    >
                      <div className="flex justify-between items-start">
                        <div>
                          <p className="font-medium text-gray-900">{account.name}</p>
                          {account.institution && (
                            <p className="text-sm text-gray-500">{account.institution}</p>
                          )}
                        </div>
                        <p className="font-semibold">{formatCurrency(account.balance)}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
