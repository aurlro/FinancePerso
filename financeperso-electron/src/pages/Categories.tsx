import * as React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

declare global {
  interface Window {
    electronAPI: {
      getCategories: () => Promise<any[]>;
    };
  }
}

export function Categories() {
  const [categories, setCategories] = React.useState<any[]>([]);
  const [loading, setLoading] = React.useState(true);

  React.useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      const data = await window.electronAPI.getCategories();
      setCategories(data);
    } catch (error) {
      console.error('Failed to load categories:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return React.createElement('div', { className: 'text-center p-8' }, 'Chargement...');
  }

  return React.createElement('div', { className: 'space-y-4' },
    React.createElement('h2', { className: 'text-2xl font-bold' }, 
      `Catégories (${categories.length})`
    ),

    React.createElement('div', { className: 'grid grid-cols-2 md:grid-cols-4 gap-4' },
      categories.map((cat) => 
        React.createElement(Card, { 
          key: cat.id,
          className: 'hover:shadow-md transition-shadow cursor-pointer'
        },
          React.createElement(CardContent, { className: 'p-6 text-center' },
            React.createElement('div', { 
              className: 'text-4xl mb-2',
              style: { color: cat.color }
            }, cat.emoji),
            React.createElement('h3', { className: 'font-medium' }, cat.name),
            cat.budget_limit && React.createElement('p', { className: 'text-sm text-muted-foreground mt-1' },
              `Budget: ${cat.budget_limit}€`
            )
          )
        )
      )
    )
  );
}
