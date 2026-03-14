import * as React from 'react';
import { HashRouter, Routes, Route } from 'react-router-dom';
import { Layout } from '@/components/Layout';
import { Dashboard } from '@/pages/Dashboard';
import { Transactions } from '@/pages/Transactions';
import { Categories } from '@/pages/Categories';
import { Budgets } from '@/pages/Budgets';
import { Settings } from '@/pages/Settings';
import { Import } from '@/pages/Import';
import { Validation } from '@/pages/Validation';
import { Members } from '@/pages/Members';
import { Assistant } from '@/pages/Assistant';
import { Subscriptions } from '@/pages/Subscriptions';
import { Wealth } from '@/pages/Wealth';

export default function App() {
  return React.createElement(HashRouter, {},
    React.createElement(Layout, {},
      React.createElement(Routes, {},
        React.createElement(Route, { path: '/', element: React.createElement(Dashboard, {}) }),
        React.createElement(Route, { path: '/transactions', element: React.createElement(Transactions, {}) }),
        React.createElement(Route, { path: '/categories', element: React.createElement(Categories, {}) }),
        React.createElement(Route, { path: '/budgets', element: React.createElement(Budgets, {}) }),
        React.createElement(Route, { path: '/members', element: React.createElement(Members, {}) }),
        React.createElement(Route, { path: '/wealth', element: React.createElement(Wealth, {}) }),
        React.createElement(Route, { path: '/subscriptions', element: React.createElement(Subscriptions, {}) }),
        React.createElement(Route, { path: '/import', element: React.createElement(Import, {}) }),
        React.createElement(Route, { path: '/validation', element: React.createElement(Validation, {}) }),
        React.createElement(Route, { path: '/settings', element: React.createElement(Settings, {}) }),
        React.createElement(Route, { path: '/assistant', element: React.createElement(Assistant, {}) })
      )
    )
  );
}
