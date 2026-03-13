import React, { useState, useEffect } from 'react';
import { Dashboard } from '@/pages/Dashboard';
import { Transactions } from '@/pages/Transactions';
import { Import } from '@/pages/Import';
import { Button } from '@/components/ui/button';
import { 
  LayoutDashboard, 
  ArrowLeftRight, 
  Upload, 
  Settings,
  Wallet,
  Moon,
  Sun
} from 'lucide-react';

type Page = 'dashboard' | 'transactions' | 'import' | 'settings';

function App() {
  const [currentPage, setCurrentPage] = useState<Page>('dashboard');
  const [version, setVersion] = useState('');
  const [isDark, setIsDark] = useState(false);
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);

  useEffect(() => {
    // Get app version
    window.electronAPI?.getVersion().then(v => setVersion(v));
    
    // Check initial theme
    window.electronAPI?.theme?.get().then(theme => {
      setIsDark(theme === 'dark');
    });
  }, []);

  const toggleTheme = async () => {
    const newTheme = isDark ? 'light' : 'dark';
    await window.electronAPI?.theme?.set(newTheme);
    setIsDark(!isDark);
  };

  const renderPage = () => {
    switch (currentPage) {
      case 'dashboard':
        return <Dashboard />;
      case 'transactions':
        return <Transactions />;
      case 'import':
        return <Import />;
      case 'settings':
        return (
          <div className="p-6">
            <h1 className="text-3xl font-bold text-gray-900">Paramètres</h1>
            <p className="text-gray-500 mt-2">Version {version}</p>
          </div>
        );
      default:
        return <Dashboard />;
    }
  };

  const navItems: { id: Page; label: string; icon: React.ReactNode }[] = [
    { id: 'dashboard', label: 'Tableau de bord', icon: <LayoutDashboard className="h-5 w-5" /> },
    { id: 'transactions', label: 'Transactions', icon: <ArrowLeftRight className="h-5 w-5" /> },
    { id: 'import', label: 'Import', icon: <Upload className="h-5 w-5" /> },
    { id: 'settings', label: 'Paramètres', icon: <Settings className="h-5 w-5" /> },
  ];

  return (
    <div className={`min-h-screen flex ${isDark ? 'dark' : ''}`}>
      {/* Sidebar */}
      <aside 
        className={`bg-gray-900 text-white flex flex-col transition-all duration-300 ${
          sidebarCollapsed ? 'w-16' : 'w-64'
        }`}
      >
        {/* Logo */}
        <div className="p-4 flex items-center gap-3 border-b border-gray-800">
          <div className="w-10 h-10 bg-emerald-500 rounded-lg flex items-center justify-center flex-shrink-0">
            <Wallet className="h-6 w-6 text-white" />
          </div>
          {!sidebarCollapsed && (
            <div>
              <h1 className="font-bold text-lg leading-tight">FinancePerso</h1>
              <p className="text-xs text-gray-400">Desktop v{version}</p>
            </div>
          )}
        </div>

        {/* Navigation */}
        <nav className="flex-1 p-2 space-y-1">
          {navItems.map((item) => (
            <button
              key={item.id}
              onClick={() => setCurrentPage(item.id)}
              className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg transition-colors ${
                currentPage === item.id
                  ? 'bg-emerald-600 text-white'
                  : 'text-gray-300 hover:bg-gray-800 hover:text-white'
              }`}
              title={sidebarCollapsed ? item.label : undefined}
            >
              {item.icon}
              {!sidebarCollapsed && <span className="font-medium">{item.label}</span>}
            </button>
          ))}
        </nav>

        {/* Footer */}
        <div className="p-2 border-t border-gray-800 space-y-1">
          <button
            onClick={toggleTheme}
            className="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-gray-300 hover:bg-gray-800 hover:text-white transition-colors"
            title={sidebarCollapsed ? (isDark ? 'Mode clair' : 'Mode sombre') : undefined}
          >
            {isDark ? <Sun className="h-5 w-5" /> : <Moon className="h-5 w-5" />}
            {!sidebarCollapsed && <span>{isDark ? 'Mode clair' : 'Mode sombre'}</span>}
          </button>
          
          <button
            onClick={() => setSidebarCollapsed(!sidebarCollapsed)}
            className="w-full flex items-center justify-center px-3 py-2.5 rounded-lg text-gray-400 hover:bg-gray-800 hover:text-white transition-colors"
            title={sidebarCollapsed ? 'Étendre' : 'Réduire'}
          >
            <span className="text-xs">
              {sidebarCollapsed ? '→' : '←'}
            </span>
          </button>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 bg-gray-50 overflow-auto">
        {renderPage()}
      </main>
    </div>
  );
}

export default App;
