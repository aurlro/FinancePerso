import { useDashboardData } from '@hooks/useDashboard';
import { TrendingUp, TrendingDown, Wallet, AlertCircle } from 'lucide-react';

export const Dashboard: React.FC = () => {
  const { data, isLoading } = useDashboardData();

  if (isLoading) {
    return <div className="animate-pulse">Chargement...</div>;
  }

  const stats = data?.stats;

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold">Tableau de bord</h1>
        <p className="text-muted-foreground">
          Vue d'ensemble de vos finances
        </p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Total Balance */}
        <div className="bg-card border rounded-lg p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-muted-foreground">Solde total</p>
              <p className="text-2xl font-bold mt-1">
                {stats?.total_balance.toLocaleString('fr-FR', {
                  style: 'currency',
                  currency: 'EUR',
                })}
              </p>
            </div>
            <div className="p-3 bg-primary/10 rounded-full">
              <Wallet className="w-6 h-6 text-primary" />
            </div>
          </div>
        </div>

        {/* Monthly Income */}
        <div className="bg-card border rounded-lg p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-muted-foreground">Revenus du mois</p>
              <p className="text-2xl font-bold mt-1 text-finance-income">
                {stats?.monthly_income.toLocaleString('fr-FR', {
                  style: 'currency',
                  currency: 'EUR',
                })}
              </p>
            </div>
            <div className="p-3 bg-finance-income/10 rounded-full">
              <TrendingUp className="w-6 h-6 text-finance-income" />
            </div>
          </div>
        </div>

        {/* Monthly Expenses */}
        <div className="bg-card border rounded-lg p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-muted-foreground">Dépenses du mois</p>
              <p className="text-2xl font-bold mt-1 text-finance-expense">
                {stats?.monthly_expenses.toLocaleString('fr-FR', {
                  style: 'currency',
                  currency: 'EUR',
                })}
              </p>
            </div>
            <div className="p-3 bg-finance-expense/10 rounded-full">
              <TrendingDown className="w-6 h-6 text-finance-expense" />
            </div>
          </div>
        </div>

        {/* Savings Rate */}
        <div className="bg-card border rounded-lg p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-muted-foreground">Taux d'épargne</p>
              <p className="text-2xl font-bold mt-1 text-finance-savings">
                {stats?.savings_rate.toFixed(1)}%
              </p>
            </div>
            <div className="p-3 bg-finance-savings/10 rounded-full">
              <AlertCircle className="w-6 h-6 text-finance-savings" />
            </div>
          </div>
        </div>
      </div>

      {/* Additional content will go here */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-card border rounded-lg p-6">
          <h2 className="text-lg font-semibold mb-4">Dépenses par catégorie</h2>
          <p className="text-muted-foreground text-sm">
            Graphique à implémenter
          </p>
        </div>

        <div className="bg-card border rounded-lg p-6">
          <h2 className="text-lg font-semibold mb-4">Tendance mensuelle</h2>
          <p className="text-muted-foreground text-sm">
            Graphique à implémenter
          </p>
        </div>
      </div>
    </div>
  );
};
