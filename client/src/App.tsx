import { Routes, Route } from 'react-router-dom';
import { Layout } from './components/Layout';
import { Dashboard } from './pages/Dashboard';
import { Transactions } from './pages/Transactions';
import { Categories } from './pages/Categories';
import { Accounts } from './pages/Accounts';
import { Budgets } from './pages/Budgets';
import { Import } from './pages/Import';
import { Settings } from './pages/Settings';

function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/transactions" element={<Transactions />} />
        <Route path="/categories" element={<Categories />} />
        <Route path="/accounts" element={<Accounts />} />
        <Route path="/budgets" element={<Budgets />} />
        <Route path="/import" element={<Import />} />
        <Route path="/settings" element={<Settings />} />
      </Routes>
    </Layout>
  );
}

export default App;
