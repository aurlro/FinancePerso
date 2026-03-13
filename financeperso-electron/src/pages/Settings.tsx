import * as React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Switch } from '@/components/ui/switch';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { 
  Brain, 
  Key, 
  CheckCircle2, 
  XCircle, 
  Loader2, 
  Sparkles,
  Server,
  Bot,
  Save,
  Database
} from 'lucide-react';
import { useAI, type AISettings } from '@/hooks/useAI';
import { UpdateChecker } from '@/components/UpdateChecker';

declare global {
  interface Window {
    electronAPI: {
      getVersion: () => Promise<string>;
      getPath: (name: string) => Promise<string>;
      platform: string;
    };
  }
}

const AI_PROVIDERS = [
  { value: 'gemini', label: 'Google Gemini', description: 'Gratuit, rapide, bonne qualité', icon: Sparkles },
  { value: 'openai', label: 'OpenAI GPT', description: 'Payant, très précis', icon: Bot },
  { value: 'local', label: 'Local uniquement', description: 'Sans API, règles simples', icon: Database },
];

export function Settings() {
  const [version, setVersion] = React.useState('');
  const [dbPath, setDbPath] = React.useState('');
  
  const { 
    settings, 
    saveSettings, 
    testConnection, 
    loading, 
    testing, 
    testResult,
    clearTestResult 
  } = useAI();

  const [localSettings, setLocalSettings] = React.useState<AISettings>({
    provider: 'gemini',
    apiKey: '',
    model: 'gemini-2.0-flash',
    enabled: false,
    autoCategorize: false,
  });
  const [hasChanges, setHasChanges] = React.useState(false);

  React.useEffect(() => {
    loadInfo();
  }, []);

  React.useEffect(() => {
    if (settings) {
      setLocalSettings(settings);
    }
  }, [settings]);

  const loadInfo = async () => {
    try {
      const [v, path] = await Promise.all([
        window.electronAPI.getVersion(),
        window.electronAPI.getPath('userData'),
      ]);
      setVersion(v);
      setDbPath(path);
    } catch (error) {
      console.error('Failed to load info:', error);
    }
  };

  const handleProviderChange = (provider: string) => {
    setLocalSettings(prev => ({ 
      ...prev, 
      provider: provider as AISettings['provider'],
      // Reset model when switching provider
      model: provider === 'gemini' ? 'gemini-2.0-flash' : 
             provider === 'openai' ? 'gpt-3.5-turbo' : ''
    }));
    setHasChanges(true);
    clearTestResult?.();
  };

  const handleApiKeyChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setLocalSettings(prev => ({ ...prev, apiKey: e.target.value }));
    setHasChanges(true);
    clearTestResult?.();
  };

  const handleToggleEnabled = (checked: boolean) => {
    setLocalSettings(prev => ({ ...prev, enabled: checked }));
    setHasChanges(true);
  };

  const handleToggleAutoCategorize = (checked: boolean) => {
    setLocalSettings(prev => ({ ...prev, autoCategorize: checked }));
    setHasChanges(true);
  };

  const handleTestConnection = async () => {
    // Sauvegarde temporaire pour le test
    await saveSettings(localSettings);
    await testConnection();
  };

  const handleSave = async () => {
    const success = await saveSettings(localSettings);
    if (success) {
      setHasChanges(false);
    }
  };

  const selectedProvider = AI_PROVIDERS.find(p => p.value === localSettings.provider);
  const ProviderIcon = selectedProvider?.icon || Sparkles;

  return React.createElement('div', { className: 'space-y-6 max-w-3xl' },
    React.createElement('h2', { className: 'text-2xl font-bold' }, 'Paramètres'),

    // Section IA
    React.createElement(Card, {},
      React.createElement(CardHeader, {},
        React.createElement('div', { className: 'flex items-center gap-2' },
          React.createElement(Brain, { className: 'h-5 w-5 text-purple-600' }),
          React.createElement(CardTitle, {}, 'Intelligence Artificielle')
        )
      ),
      React.createElement(CardContent, { className: 'space-y-6' },
        // Activation IA
        React.createElement('div', { className: 'flex items-center justify-between' },
          React.createElement('div', { className: 'space-y-0.5' },
            React.createElement(Label, { htmlFor: 'ai-enabled', className: 'text-base' }, 
              'Activer la catégorisation IA'
            ),
            React.createElement('p', { className: 'text-sm text-muted-foreground' },
              'Utilise l\'IA pour suggérer automatiquement des catégories'
            )
          ),
          React.createElement(Switch, {
            id: 'ai-enabled',
            checked: localSettings.enabled,
            onCheckedChange: handleToggleEnabled,
          })
        ),

        // Provider selection
        React.createElement('div', { className: 'space-y-2' },
          React.createElement(Label, {}, 'Fournisseur d\'IA'),
          React.createElement(Select, {
            value: localSettings.provider,
            onValueChange: handleProviderChange,
            disabled: !localSettings.enabled,
          },
            React.createElement(SelectTrigger, { className: 'w-full' },
              React.createElement(SelectValue, {})
            ),
            React.createElement(SelectContent, {},
              AI_PROVIDERS.map(provider => 
                React.createElement(SelectItem, { 
                  key: provider.value, 
                  value: provider.value 
                },
                  React.createElement('div', { className: 'flex items-center gap-2' },
                    React.createElement(provider.icon, { className: 'h-4 w-4' }),
                    React.createElement('span', {}, provider.label),
                    React.createElement('span', { className: 'text-xs text-muted-foreground ml-2' },
                      provider.description
                    )
                  )
                )
              )
            )
          )
        ),

        // API Key
        localSettings.provider !== 'local' && React.createElement('div', { className: 'space-y-2' },
          React.createElement(Label, { htmlFor: 'api-key', className: 'flex items-center gap-2' },
            React.createElement(Key, { className: 'h-4 w-4' }),
            'Clé API'
          ),
          React.createElement('div', { className: 'flex gap-2' },
            React.createElement(Input, {
              id: 'api-key',
              type: 'password',
              placeholder: localSettings.provider === 'gemini' 
                ? 'Votre clé API Gemini...' 
                : 'Votre clé API OpenAI...',
              value: localSettings.apiKey,
              onChange: handleApiKeyChange,
              disabled: !localSettings.enabled,
              className: 'flex-1',
            }),
            React.createElement(Button, {
              variant: 'outline',
              onClick: handleTestConnection,
              disabled: !localSettings.enabled || !localSettings.apiKey || testing,
            },
              testing 
                ? React.createElement(Loader2, { className: 'h-4 w-4 animate-spin' })
                : 'Tester'
            )
          ),
          React.createElement('p', { className: 'text-xs text-muted-foreground' },
            localSettings.provider === 'gemini' 
              ? 'Obtenez une clé gratuite sur makersuite.google.com'
              : 'Votre clé API reste stockée localement sur votre ordinateur.'
          )
        ),

        // Test result
        testResult && React.createElement(Alert, { 
          variant: testResult.success ? 'default' : 'destructive',
          className: 'mt-2'
        },
          testResult.success 
            ? React.createElement(CheckCircle2, { className: 'h-4 w-4' })
            : React.createElement(XCircle, { className: 'h-4 w-4' }),
          React.createElement(AlertDescription, {}, testResult.message)
        ),

        // Auto-categorization
        React.createElement('div', { 
          className: 'flex items-center justify-between pt-4 border-t'
        },
          React.createElement('div', { className: 'space-y-0.5' },
            React.createElement(Label, { htmlFor: 'auto-cat', className: 'text-base' }, 
              'Catégorisation automatique'
            ),
            React.createElement('p', { className: 'text-sm text-muted-foreground' },
              'Catégorise automatiquement après chaque import CSV'
            )
          ),
          React.createElement(Switch, {
            id: 'auto-cat',
            checked: localSettings.autoCategorize,
            onCheckedChange: handleToggleAutoCategorize,
            disabled: !localSettings.enabled,
          })
        ),

        // Save button
        hasChanges && React.createElement('div', { className: 'flex justify-end pt-4' },
          React.createElement(Button, {
            onClick: handleSave,
            disabled: loading,
            className: 'bg-emerald-600 hover:bg-emerald-700',
          },
            loading 
              ? React.createElement(Loader2, { className: 'h-4 w-4 animate-spin mr-2' })
              : React.createElement(Save, { className: 'h-4 w-4 mr-2' }),
            'Sauvegarder les paramètres'
          )
        )
      )
    ),

    // Section Mises à jour
    React.createElement(UpdateChecker, {}),

    // Section À propos
    React.createElement(Card, {},
      React.createElement(CardHeader, {},
        React.createElement(CardTitle, {}, 'À propos')
      ),
      React.createElement(CardContent, { className: 'space-y-2' },
        React.createElement('div', { className: 'flex justify-between' },
          React.createElement('span', { className: 'text-muted-foreground' }, 'Version'),
          React.createElement('span', { className: 'font-medium' }, version)
        ),
        React.createElement('div', { className: 'flex justify-between' },
          React.createElement('span', { className: 'text-muted-foreground' }, 'Plateforme'),
          React.createElement('span', { className: 'font-medium' }, window.electronAPI?.platform)
        ),
        React.createElement('div', { className: 'flex justify-between' },
          React.createElement('span', { className: 'text-muted-foreground' }, 'Base de données'),
          React.createElement('span', { className: 'font-medium text-sm' }, `${dbPath}/finance.db`)
        )
      )
    ),

    // Section Stockage
    React.createElement(Card, {},
      React.createElement(CardHeader, {},
        React.createElement(CardTitle, {}, 'Stockage')
      ),
      React.createElement(CardContent, {},
        React.createElement('p', { className: 'text-sm text-muted-foreground' },
          'Les données sont stockées localement dans une base SQLite. Tout reste sur votre ordinateur.',
          React.createElement('br', {}),
          'Vos clés API ne sont jamais envoyées ailleurs que vers les services choisis.'
        )
      )
    )
  );
}
