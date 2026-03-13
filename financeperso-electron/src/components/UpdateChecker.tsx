import { useEffect, useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Download, RefreshCw, CheckCircle, AlertCircle, Info } from 'lucide-react';

interface UpdateInfo {
  version: string;
  releaseDate?: string;
  releaseNotes?: string;
}

export function UpdateChecker() {
  const [status, setStatus] = useState<'idle' | 'checking' | 'available' | 'downloading' | 'downloaded' | 'not-available' | 'error'>('idle');
  const [updateInfo, setUpdateInfo] = useState<UpdateInfo | null>(null);
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // Écouter les événements de mise à jour
    const setupListeners = () => {
      if (!window.electronAPI?.update) return;

      window.electronAPI.update.onChecking(() => {
        setStatus('checking');
      });

      window.electronAPI.update.onAvailable((info) => {
        setStatus('available');
        setUpdateInfo(info);
      });

      window.electronAPI.update.onNotAvailable(() => {
        setStatus('not-available');
      });

      window.electronAPI.update.onProgress((percent) => {
        setStatus('downloading');
        setProgress(percent);
      });

      window.electronAPI.update.onDownloaded((info) => {
        setStatus('downloaded');
        setUpdateInfo(info);
      });

      window.electronAPI.update.onError((message) => {
        setStatus('error');
        setError(message);
      });
    };

    setupListeners();
  }, []);

  const checkForUpdates = () => {
    window.electronAPI?.update?.check();
    setStatus('checking');
  };

  const downloadUpdate = () => {
    window.electronAPI?.update?.download();
    setStatus('downloading');
  };

  const installUpdate = () => {
    window.electronAPI?.update?.install();
  };

  const renderContent = () => {
    switch (status) {
      case 'checking':
        return (
          <div className="flex items-center gap-3 text-muted-foreground">
            <RefreshCw className="h-5 w-5 animate-spin" />
            <span>Recherche de mises à jour...</span>
          </div>
        );

      case 'available':
        return (
          <div className="space-y-4">
            <div className="flex items-center gap-2">
              <Badge variant="warning" className="gap-1">
                <Info className="h-3 w-3" />
                Nouvelle version
              </Badge>
              <span className="font-semibold">{updateInfo?.version}</span>
            </div>
            <p className="text-sm text-muted-foreground">
              Une nouvelle version est disponible. Voulez-vous la télécharger ?
            </p>
            <Button onClick={downloadUpdate} className="w-full">
              <Download className="mr-2 h-4 w-4" />
              Télécharger la mise à jour
            </Button>
          </div>
        );

      case 'downloading':
        return (
          <div className="space-y-4">
            <div className="flex items-center justify-between text-sm">
              <span className="text-muted-foreground">Téléchargement...</span>
              <span className="font-medium">{progress}%</span>
            </div>
            <Progress value={progress} className="h-2" />
          </div>
        );

      case 'downloaded':
        return (
          <div className="space-y-4">
            <div className="flex items-center gap-2 text-green-600">
              <CheckCircle className="h-5 w-5" />
              <span className="font-medium">Mise à jour prête</span>
            </div>
            <p className="text-sm text-muted-foreground">
              La version {updateInfo?.version} est prête à être installée.
            </p>
            <Button onClick={installUpdate} className="w-full">
              Redémarrer et installer
            </Button>
          </div>
        );

      case 'not-available':
        return (
          <div className="flex items-center gap-2 text-muted-foreground">
            <CheckCircle className="h-5 w-5 text-green-500" />
            <span>Application à jour</span>
          </div>
        );

      case 'error':
        return (
          <div className="space-y-4">
            <div className="flex items-center gap-2 text-red-600">
              <AlertCircle className="h-5 w-5" />
              <span className="font-medium">Erreur</span>
            </div>
            <p className="text-sm text-muted-foreground">{error}</p>
            <Button onClick={checkForUpdates} variant="outline" className="w-full">
              Réessayer
            </Button>
          </div>
        );

      default:
        return (
          <div className="space-y-4">
            <p className="text-sm text-muted-foreground">
              Vérifiez si une nouvelle version est disponible.
            </p>
            <Button onClick={checkForUpdates} variant="outline" className="w-full">
              <RefreshCw className="mr-2 h-4 w-4" />
              Vérifier les mises à jour
            </Button>
          </div>
        );
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <RefreshCw className="h-5 w-5" />
          Mises à jour
        </CardTitle>
        <CardDescription>
          Gérez les mises à jour de l'application
        </CardDescription>
      </CardHeader>
      <CardContent>{renderContent()}</CardContent>
    </Card>
  );
}
