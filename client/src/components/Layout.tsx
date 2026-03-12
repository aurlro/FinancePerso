import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  Receipt,
  Tags,
  Wallet,
  PiggyBank,
  Upload,
  Settings,
} from 'lucide-react';

interface LayoutProps {
  children: React.ReactNode;
}

const navItems = [
  { to: '/', icon: LayoutDashboard, label: 'Tableau de bord' },
  { to: '/transactions', icon: Receipt, label: 'Transactions' },
  { to: '/categories', icon: Tags, label: 'Catégories' },
  { to: '/accounts', icon: Wallet, label: 'Comptes' },
  { to: '/budgets', icon: PiggyBank, label: 'Budgets' },
  { to: '/import', icon: Upload, label: 'Import' },
];

export const Layout: React.FC<LayoutProps> = ({ children }) => {
  return (
    <div className="min-h-screen bg-background flex">
      {/* Sidebar */}
      <aside className="w-64 bg-card border-r border-border flex-shrink-0">
        <div className="p-6">
          <h1 className="text-2xl font-bold text-primary flex items-center gap-2">
            <span className="text-3xl">💰</span>
            FinancePerso
          </h1>
          <p className="text-xs text-muted-foreground mt-1">v6.0.0</p>
        </div>

        <nav className="px-4 pb-4">
          <ul className="space-y-1">
            {navItems.map((item) => (
              <li key={item.to}>
                <NavLink
                  to={item.to}
                  className={({ isActive }) =>
                    `flex items-center gap-3 px-4 py-3 rounded-lg text-sm font-medium transition-colors ${
                      isActive
                        ? 'bg-primary text-primary-foreground'
                        : 'text-muted-foreground hover:bg-muted hover:text-foreground'
                    }`
                  }
                >
                  <item.icon className="w-5 h-5" />
                  {item.label}
                </NavLink>
              </li>
            ))}
          </ul>

          <div className="mt-8 pt-4 border-t border-border">
            <NavLink
              to="/settings"
              className={({ isActive }) =>
                `flex items-center gap-3 px-4 py-3 rounded-lg text-sm font-medium transition-colors ${
                  isActive
                    ? 'bg-primary text-primary-foreground'
                    : 'text-muted-foreground hover:bg-muted hover:text-foreground'
                }`
              }
            >
              <Settings className="w-5 h-5" />
              Paramètres
            </NavLink>
          </div>
        </nav>
      </aside>

      {/* Main content */}
      <main className="flex-1 overflow-auto">
        <div className="p-8 max-w-7xl mx-auto">{children}</div>
      </main>
    </div>
  );
};
