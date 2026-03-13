import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { useDashboard } from '@/hooks/useDashboard';
import { 
  TrendingUp, 
  TrendingDown, 
  Wallet,
  Calendar,
  RefreshCw,
  Loader2
} from 'lucide-react';

export function Dashboard() {
  const today = new Date();
  const [year, setYear] = useState(today.getFullYear());
  const [month, setMonth] = useState(today.getMonth() + 1);
  
  const { stats, loading, error, refresh } = useDashboard(year, month);

  const monthNames = [
    'Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin',
    'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre'
  ];

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('fr-FR', {
      style: 'currency',
      currency: 'EUR'
    }).format(amount);
  };

  const handlePreviousMonth = () => {
    if (month === 1) {
      setMonth(12);
      setYear(year - 1);
    } else {
      setMonth(month - 1);
    }
  };

  const handleNextMonth = () => {
    if (month === 12) {
      setMonth(1);
      setYear(year + 1);
    } else {
      setMonth(month + 1);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="h-8 w-8 animate-spin text-emerald-600" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-6">
        <div className="bg-red-50 border border-red-200 text-red-800 p-4 rounded-lg">
          <p>Erreur: {error}</p>
          <Button onClick={refresh} variant="outline" className="mt-2">
            Réessayer
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Tableau de bord</h1>
          <p className="text-gray-500">Vue d'ensemble de vos finances</p>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="outline" size="icon" onClick={handlePreviousMonth}>
            ←
          </Button>
          <div className="flex items-center gap-2 px-4 py-2 bg-gray-100 rounded-lg">
            <Calendar className="h-4 w-4 text-gray-500" />
            <span className="font-medium">
              {monthNames[month - 1]} {year}
            </span>
          </div>
          <Button variant="outline" size="icon" onClick={handleNextMonth}>
            →
          </Button>
          <Button variant="outline" size="icon" onClick={refresh}>
            <RefreshCw className="h-4 w-4" />
          </Button>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-gray-500">
              Revenus
            </CardTitle>
            <TrendingUp className="h-4 w-4 text-emerald-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-emerald-600">
              {formatCurrency(stats?.stats.total_income || 0)}
            </div>
            <p className="text-xs text-gray-500">Ce mois</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-gray-500">
              Dépenses
            </CardTitle>
            <TrendingDown className="h-4 w-4 text-red-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-red-600">
              {formatCurrency(stats?.stats.total_expense || 0)}
            </div>
            <p className="text-xs text-gray-500">Ce mois</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-gray-500">
              Solde
            </CardTitle>
            <Wallet className="h-4 w-4 text-blue-500" />
          </CardHeader>
          <CardContent>
            <div className={`text-2xl font-bold ${
              (stats?.stats.balance || 0) >= 0 ? 'text-blue-600' : 'text-red-600'
            }`}>
              {formatCurrency(stats?.stats.balance || 0)}
            </div>
            <p className="text-xs text-gray-500">Différence</p>
          </CardContent>
        </Card>
      </div>

      {/* Dépenses par catégorie */}
      <Card>
        <CardHeader>
          <CardTitle>Dépenses par catégorie</CardTitle>
        </CardHeader>
        <CardContent>
          {stats?.byCategory && stats.byCategory.length > 0 ? (
            <div className="space-y-3">
              {stats.byCategory.map((item, index) => (
                <div key={index} className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div 
                      className="w-3 h-3 rounded-full"
                      style={{ 
                        backgroundColor: [
                          '#10B981', '#3B82F6', '#8B5CF6', '#F59E0B', 
                          '#EF4444', '#EC4899', '#06B6D4', '#84CC16'
                        ][index % 8]
                      }}
                    />
                    <span className="font-medium">{item.category || 'Non catégorisé'}</span>
                  </div>
                  <div className="flex items-center gap-4">
                    <div className="w-32 h-2 bg-gray-100 rounded-full overflow-hidden">
                      <div 
                        className="h-full bg-gray-800 rounded-full"
                        style={{ 
                          width: `${Math.min((item.total / (stats?.stats.total_expense || 1)) * 100, 100)}%`,
                          backgroundColor: [
                            '#10B981', '#3B82F6', '#8B5CF6', '#F59E0B', 
                            '#EF4444', '#EC4899', '#06B6D4', '#84CC16'
                          ][index % 8]
                        }}
                      />
                    </div>
                    <span className="font-medium w-24 text-right">
                      {formatCurrency(item.total)}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-gray-500 text-center py-8">
              Aucune dépense ce mois-ci
            </p>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
