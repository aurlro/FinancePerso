import * as React from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { useWealthAccounts } from '@/hooks/useWealth';

// Icons
const WalletIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M21 12V7H5a2 2 0 0 1 0-4h14v4"/><path d="M3 5v14a2 2 0 0 0 2 2h16v-5"/>
    <path d="M18 12a2 2 0 0 0 0 4h4v-4Z"/>
  </svg>
);

const PiggyBankIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M19 5c-1.5 0-2.8 1.4-3 2-3.5-1.5-11-.3-11 5 0 1.8 0 3 2 4.5V20h4v-2h3v2h4v-4c1-.5 1.7-1 2-2h2v-4h-2c0-1-.5-1.5-1-2h0V5z"/>
    <path d="M2 9v1c0 1.1.9 2 2 2h1"/>
    <path d="M16 11h0"/>
  </svg>
);

const TrendingUpIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <polyline points="23 6 13.5 15.5 8.5 10.5 1 18"/><polyline points="17 6 23 6 23 12"/>
  </svg>
);

const BitcoinIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M11.767 19.089c4.924.868 6.14-6.025 1.216-6.894m-1.216 6.894L5.86 18.047m5.908 1.042-.347 1.97m1.563-8.864c4.924.869 6.14-6.025 1.215-6.893m-1.215 6.893-3.94-.694m5.155-6.2L8.29 4.26m5.908 1.042.348-1.97M7.48 20.364l3.126-17.727"/>
  </svg>
);

// Format currency
const formatCurrency = (amount: number) => {
  return new Intl.NumberFormat('fr-FR', {
    style: 'currency',
    currency: 'EUR',
  }).format(amount);
};

// Composant pour les KPI Cards avec animation
interface KPICardProps {
  title: string;
  amount: number;
  icon: React.ReactNode;
  color: string;
  trend?: number;
}

function KPICard({ title, amount, icon, color, trend }: KPICardProps) {
  const [displayAmount, setDisplayAmount] = React.useState(0);
  
  React.useEffect(() => {
    // Animation de comptage
    const duration = 1000;
    const steps = 30;
    const increment = amount / steps;
    let current = 0;
    
    const timer = setInterval(() => {
      current += increment;
      if (current >= amount) {
        setDisplayAmount(amount);
        clearInterval(timer);
      } else {
        setDisplayAmount(current);
      }
    }, duration / steps);
    
    return () => clearInterval(timer);
  }, [amount]);

  return (
    <Card className="relative overflow-hidden">
      <CardContent className="p-6">
        <div className="flex items-start justify-between">
          <div className={`p-3 rounded-xl ${color} bg-opacity-10`}>
            <div className={`${color.replace('bg-', 'text-')}`}>
              {icon}
            </div>
          </div>
          {trend !== undefined && trend !== 0 && (
            <div className={`flex items-center gap-1 text-sm ${trend > 0 ? 'text-emerald-600' : 'text-red-600'}`}>
              <span>{trend > 0 ? '+' : ''}{trend}%</span>
            </div>
          )}
        </div>
        <div className="mt-4">
          <p className="text-sm text-gray-500">{title}</p>
          <p className="text-2xl font-bold text-gray-900">
            {formatCurrency(displayAmount)}
          </p>
        </div>
      </CardContent>
    </Card>
  );
}

export function WealthOverview() {
  const { stats, isLoading } = useWealthAccounts();

  if (isLoading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {[1, 2, 3, 4].map((i) => (
          <Card key={i} className="animate-pulse">
            <CardContent className="p-6 space-y-4">
              <div className="h-12 w-12 bg-gray-200 rounded-xl"></div>
              <div className="h-4 bg-gray-200 rounded w-1/2"></div>
              <div className="h-8 bg-gray-200 rounded w-3/4"></div>
            </CardContent>
          </Card>
        ))}
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      <KPICard
        title="Patrimoine total"
        amount={stats.totalWealth}
        icon={<WalletIcon />}
        color="bg-blue-500"
        trend={stats.yearlyChange}
      />
      <KPICard
        title="Liquidités"
        amount={stats.totalChecking}
        icon={<PiggyBankIcon />}
        color="bg-blue-500"
      />
      <KPICard
        title="Épargne"
        amount={stats.totalSavings}
        icon={<TrendingUpIcon />}
        color="bg-emerald-500"
      />
      <KPICard
        title="Investissements"
        amount={stats.totalInvestments + stats.totalCrypto}
        icon={<BitcoinIcon />}
        color="bg-violet-500"
      />
    </div>
  );
}
