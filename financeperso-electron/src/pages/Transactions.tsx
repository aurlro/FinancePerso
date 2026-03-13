import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { useTransactions } from '@/hooks/useTransactions';
import { 
  ArrowUpDown, 
  Calendar, 
  Tag, 
  RefreshCw, 
  Loader2,
  ChevronLeft,
  ChevronRight,
  Search
} from 'lucide-react';

export function Transactions() {
  const today = new Date();
  const [year, setYear] = useState(today.getFullYear());
  const [month, setMonth] = useState(today.getMonth() + 1);
  const [search, setSearch] = useState('');
  
  const { transactions, loading, error, refresh } = useTransactions({ year, month });

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

  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr);
    return new Intl.DateTimeFormat('fr-FR', {
      day: '2-digit',
      month: 'short'
    }).format(date);
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

  // Filtrer par recherche
  const filteredTransactions = transactions.filter(tx => 
    tx.label.toLowerCase().includes(search.toLowerCase()) ||
    (tx.category && tx.category.toLowerCase().includes(search.toLowerCase()))
  );

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
          <h1 className="text-3xl font-bold text-gray-900">Transactions</h1>
          <p className="text-gray-500">Gérez vos opérations bancaires</p>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="outline" size="icon" onClick={handlePreviousMonth}>
            <ChevronLeft className="h-4 w-4" />
          </Button>
          <div className="flex items-center gap-2 px-4 py-2 bg-gray-100 rounded-lg">
            <Calendar className="h-4 w-4 text-gray-500" />
            <span className="font-medium">
              {monthNames[month - 1]} {year}
            </span>
          </div>
          <Button variant="outline" size="icon" onClick={handleNextMonth}>
            <ChevronRight className="h-4 w-4" />
          </Button>
          <Button variant="outline" size="icon" onClick={refresh}>
            <RefreshCw className="h-4 w-4" />
          </Button>
        </div>
      </div>

      {/* Search */}
      <div className="relative">
        <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
        <input
          type="text"
          placeholder="Rechercher une transaction..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="w-full pl-10 pr-4 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500"
        />
      </div>

      {/* Table */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center justify-between">
            <span>Liste des transactions</span>
            <span className="text-sm font-normal text-gray-500">
              {filteredTransactions.length} transaction{filteredTransactions.length !== 1 ? 's' : ''}
            </span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          {filteredTransactions.length > 0 ? (
            <div className="divide-y">
              {filteredTransactions.map((tx) => (
                <div 
                  key={tx.id} 
                  className="py-3 flex items-center justify-between hover:bg-gray-50 px-2 rounded-lg transition-colors"
                >
                  <div className="flex items-center gap-3">
                    {/* Icon/Emoji */}
                    <div 
                      className="w-10 h-10 rounded-full flex items-center justify-center text-lg"
                      style={{ backgroundColor: tx.color ? `${tx.color}20` : '#F3F4F6' }}
                    >
                      {tx.emoji || (tx.type === 'credit' ? '💰' : '💳')}
                    </div>
                    
                    {/* Info */}
                    <div>
                      <p className="font-medium text-gray-900">{tx.label}</p>
                      <div className="flex items-center gap-2 text-sm text-gray-500">
                        <span>{formatDate(tx.date)}</span>
                        {tx.category && (
                          <>
                            <span>•</span>
                            <span className="flex items-center gap-1">
                              <Tag className="h-3 w-3" />
                              {tx.category}
                            </span>
                          </>
                        )}
                      </div>
                    </div>
                  </div>
                  
                  {/* Amount */}
                  <div className={`font-semibold ${
                    tx.type === 'credit' ? 'text-emerald-600' : 'text-gray-900'
                  }`}>
                    {tx.type === 'credit' ? '+' : '-'}{formatCurrency(tx.amount)}
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-12">
              <div className="w-12 h-12 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-3">
                <ArrowUpDown className="h-6 w-6 text-gray-400" />
              </div>
              <p className="text-gray-500">Aucune transaction ce mois-ci</p>
              <p className="text-sm text-gray-400 mt-1">
                Importez un relevé bancaire pour commencer
              </p>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
