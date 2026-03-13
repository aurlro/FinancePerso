import * as React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

declare global {
  interface Window {
    electronAPI: {
      getAllTransactions: (limit?: number, offset?: number) => Promise<any[]>;
      createTransaction: (data: any) => Promise<any>;
      getCategories: () => Promise<any[]>;
    };
  }
}

export function TransactionList() {
  const [transactions, setTransactions] = React.useState<any[]>([]);
  const [categories, setCategories] = React.useState<any[]>([]);
  const [loading, setLoading] = React.useState(true);

  React.useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      const [txData, catData] = await Promise.all([
        window.electronAPI.getAllTransactions(10, 0),
        window.electronAPI.getCategories(),
      ]);
      setTransactions(txData);
      setCategories(catData);
    } catch (error) {
      console.error('Failed to load data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleAddTest = async () => {
    try {
      await window.electronAPI.createTransaction({
        date: new Date().toISOString().split('T')[0],
        description: 'Transaction test',
        amount: Math.round(Math.random() * 100),
        category: categories[0]?.name || 'Autre',
        type: 'expense',
        account: 'Compte principal',
        notes: '',
      });
      loadData();
    } catch (error) {
      console.error('Failed to create transaction:', error);
    }
  };

  if (loading) {
    return React.createElement('div', { className: 'text-center p-4' }, 'Chargement...');
  }

  return React.createElement(Card, {},
    React.createElement(CardHeader, {},
      React.createElement(CardTitle, {}, `Transactions (${transactions.length})`)
    ),
    React.createElement(CardContent, {},
      React.createElement('div', { className: 'space-y-4' },
        transactions.length === 0 
          ? React.createElement('p', { className: 'text-muted-foreground' }, 'Aucune transaction')
          : transactions.map((tx) => 
              React.createElement('div', { 
                key: tx.id, 
                className: 'flex justify-between items-center p-3 bg-gray-50 rounded-lg'
              },
                React.createElement('div', {},
                  React.createElement('p', { className: 'font-medium' }, tx.description),
                  React.createElement('p', { className: 'text-sm text-gray-500' }, 
                    `${tx.date} • ${tx.category}`
                  )
                ),
                React.createElement('span', { 
                  className: `font-bold ${tx.type === 'expense' ? 'text-red-500' : 'text-green-500'}`
                }, 
                  `${tx.type === 'expense' ? '-' : '+'}${tx.amount}€`
                )
              )
            ),
        React.createElement('button', {
          onClick: handleAddTest,
          className: 'w-full py-2 px-4 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 transition-colors'
        }, 'Ajouter une transaction test')
      )
    )
  );
}
