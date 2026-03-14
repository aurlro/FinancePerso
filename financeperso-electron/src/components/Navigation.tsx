import * as React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { cn } from '@/lib/utils';

const navItems = [
  { path: '/', label: 'Dashboard', icon: '📊', exact: true },
  { path: '/transactions', label: 'Transactions', icon: '💳' },
  { path: '/subscriptions', label: 'Abonnements', icon: '📅' },
  { path: '/budgets', label: 'Budgets', icon: '🎯' },
  { path: '/categories', label: 'Catégories', icon: '📁' },
  { path: '/members', label: 'Membres', icon: '👥' },
  { path: '/wealth', label: 'Patrimoine', icon: '💰' },
  { path: '/assistant', label: 'Assistant IA', icon: '🤖' },
  { path: '/import', label: 'Import', icon: '📥' },
  { path: '/validation', label: 'Validation', icon: '✅' },
  { path: '/settings', label: 'Paramètres', icon: '⚙️' },
];

interface NavigationProps {
  orientation?: 'horizontal' | 'vertical';
  onItemClick?: () => void;
  className?: string;
}

export function Navigation({
  orientation = 'horizontal',
  onItemClick,
  className,
}: NavigationProps) {
  const location = useLocation();

  const isActive = (item: typeof navItems[0]) => {
    return item.exact
      ? location.pathname === item.path
      : location.pathname.startsWith(item.path);
  };

  if (orientation === 'vertical') {
    return (
      <nav className={cn('space-y-1 px-3', className)}>
        {navItems.map((item) => {
          const active = isActive(item);
          return (
            <Link
              key={item.path}
              to={item.path}
              onClick={onItemClick}
              className={cn(
                'flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors',
                active
                  ? 'bg-emerald-50 text-emerald-700'
                  : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
              )}
            >
              <span className="text-lg">{item.icon}</span>
              {item.label}
            </Link>
          );
        })}
      </nav>
    );
  }

  // Horizontal orientation (mobile bottom nav)
  return (
    <nav className={cn('flex items-center justify-around px-2 py-2', className)}>
      {navItems.slice(0, 5).map((item) => {
        const active = isActive(item);
        return (
          <Link
            key={item.path}
            to={item.path}
            onClick={onItemClick}
            className={cn(
              'flex flex-col items-center gap-1 rounded-lg px-3 py-1.5 text-xs font-medium transition-colors',
              active
                ? 'text-emerald-600'
                : 'text-gray-500 hover:text-gray-700'
            )}
          >
            <span className="text-lg">{item.icon}</span>
            <span className="sr-only sm:not-sr-only">{item.label}</span>
          </Link>
        );
      })}
    </nav>
  );
}

// Legacy Navigation for backward compatibility (top bar)
export function TopNavigation() {
  const location = useLocation();

  return (
    <nav className="bg-white border-b border-gray-200 sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          <Link
            to="/"
            className="flex items-center gap-2 text-xl font-bold text-emerald-700"
          >
            🌿 FinancePerso
          </Link>

          <div className="flex items-center gap-1">
            {navItems.map((item) => {
              const active = item.exact
                ? location.pathname === item.path
                : location.pathname.startsWith(item.path);

              return (
                <Link
                  key={item.path}
                  to={item.path}
                  className={cn(
                    'px-4 py-2 rounded-lg text-sm font-medium transition-colors',
                    active
                      ? 'bg-emerald-100 text-emerald-800'
                      : 'text-gray-600 hover:bg-gray-100'
                  )}
                >
                  {item.label}
                </Link>
              );
            })}
          </div>
        </div>
      </div>
    </nav>
  );
}
