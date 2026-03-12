import { useState } from 'react';
import { useTransactions } from '@hooks/useTransactions';
import { format } from 'date-fns';
import { fr } from 'date-fns/locale';
import { ArrowUpDown, Check, Filter } from 'lucide-react';

export const Transactions: React.FC = () => {
  const [filters, setFilters] = useState({
    status: undefined as 'pending' | 'validated' | undefined,
  });

  const { data, isLoading } = useTransactions(filters);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Transactions</h1>
          <p className="text-muted-foreground">
            {data?.total || 0} transactions
          </p>
        </div>

        <div className="flex items-center gap-2">
          <button className="flex items-center gap-2 px-4 py-2 border rounded-lg hover:bg-muted">
            <Filter className="w-4 h-4" />
            Filtres
          </button>
          <button className="flex items-center gap-2 px-4 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90">
            + Nouvelle transaction
          </button>
        </div>
      </div>

      {/* Filters */}
      <div className="flex items-center gap-2">
        <button
          onClick={() => setFilters({ status: undefined })}
          className={`px-3 py-1.5 rounded-full text-sm ${
            !filters.status
              ? 'bg-primary text-primary-foreground'
              : 'bg-muted hover:bg-muted/80'
          }`}
        >
          Toutes
        </button>
        <button
          onClick={() => setFilters({ status: 'pending' })}
          className={`px-3 py-1.5 rounded-full text-sm ${
            filters.status === 'pending'
              ? 'bg-primary text-primary-foreground'
              : 'bg-muted hover:bg-muted/80'
          }`}
        >
          À valider
        </button>
        <button
          onClick={() => setFilters({ status: 'validated' })}
          className={`px-3 py-1.5 rounded-full text-sm ${
            filters.status === 'validated'
              ? 'bg-primary text-primary-foreground'
              : 'bg-muted hover:bg-muted/80'
          }`}
        >
          Validées
        </button>
      </div>

      {/* Table */}
      {isLoading ? (
        <div className="animate-pulse space-y-2">
          {[...Array(5)].map((_, i) => (
            <div key={i} className="h-14 bg-muted rounded-lg" />
          ))}
        </div>
      ) : (
        <div className="bg-card border rounded-lg overflow-hidden">
          <table className="w-full">
            <thead className="bg-muted/50">
              <tr>
                <th className="px-4 py-3 text-left text-sm font-medium">
                  <button className="flex items-center gap-1">
                    Date <ArrowUpDown className="w-3 h-3" />
                  </button>
                </th>
                <th className="px-4 py-3 text-left text-sm font-medium">Description</th>
                <th className="px-4 py-3 text-left text-sm font-medium">Catégorie</th>
                <th className="px-4 py-3 text-right text-sm font-medium">Montant</th>
                <th className="px-4 py-3 text-center text-sm font-medium">Statut</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {data?.items.map((transaction) => (
                <tr key={transaction.id} className="hover:bg-muted/30">
                  <td className="px-4 py-3 text-sm">
                    {format(new Date(transaction.date), 'dd MMM yyyy', { locale: fr })}
                  </td>
                  <td className="px-4 py-3">
                    <div>
                      <p className="text-sm font-medium">{transaction.description}</p>
                      {transaction.beneficiary && (
                        <p className="text-xs text-muted-foreground">
                          {transaction.beneficiary}
                        </p>
                      )}
                    </div>
                  </td>
                  <td className="px-4 py-3">
                    {transaction.category ? (
                      <span
                        className="inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs"
                        style={{
                          backgroundColor: `${transaction.category.color}20`,
                          color: transaction.category.color,
                        }}
                      >
                        {transaction.category.emoji} {transaction.category.name}
                      </span>
                    ) : (
                      <span className="text-xs text-muted-foreground">Non catégorisé</span>
                    )}
                  </td>
                  <td
                    className={`px-4 py-3 text-right text-sm font-medium ${
                      transaction.type === 'income'
                        ? 'text-finance-income'
                        : 'text-finance-expense'
                    }`}
                  >
                    {transaction.type === 'income' ? '+' : '-'}
                    {transaction.amount.toLocaleString('fr-FR', {
                      style: 'currency',
                      currency: 'EUR',
                    })}
                  </td>
                  <td className="px-4 py-3 text-center">
                    {transaction.is_validated ? (
                      <span className="inline-flex items-center gap-1 text-xs text-finance-income">
                        <Check className="w-3 h-3" /> Validé
                      </span>
                    ) : (
                      <span className="inline-flex items-center px-2 py-1 rounded-full text-xs bg-finance-warning/20 text-finance-warning">
                        À valider
                      </span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};
