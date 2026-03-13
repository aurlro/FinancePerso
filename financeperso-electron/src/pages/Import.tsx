import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { useElectron } from '@/hooks/useElectron';
import { 
  Upload, 
  FileText, 
  CheckCircle, 
  AlertCircle, 
  Loader2,
  RefreshCw
} from 'lucide-react';
import type { ImportResult } from '@/types';

export function Import() {
  const electron = useElectron();
  const [importing, setImporting] = useState(false);
  const [result, setResult] = useState<ImportResult | null>(null);
  const [recentImports, setRecentImports] = useState<ImportResult[]>([]);

  const handleSelectFile = async () => {
    try {
      setImporting(true);
      setResult(null);
      
      // Ouvrir le dialog de sélection de fichier
      const filePath = await electron.selectCSV();
      
      if (!filePath) {
        setImporting(false);
        return;
      }
      
      console.log('[Import] Selected file:', filePath);
      
      // Importer le fichier
      const importResult = await electron.importCSV(filePath, {
        delimiter: ';', // Détection automatique si échoue
        encoding: 'utf-8'
      });
      
      console.log('[Import] Result:', importResult);
      
      setResult(importResult);
      
      if (importResult.success) {
        setRecentImports(prev => [importResult, ...prev.slice(0, 4)]);
      }
    } catch (error) {
      console.error('[Import] Error:', error);
      setResult({
        success: false,
        error: error instanceof Error ? error.message : 'Erreur inconnue'
      });
    } finally {
      setImporting(false);
    }
  };

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Import CSV</h1>
        <p className="text-gray-500">Importez vos relevés bancaires</p>
      </div>

      {/* Zone d'import */}
      <Card>
        <CardContent className="p-8">
          <div className="flex flex-col items-center justify-center text-center space-y-4">
            <div className="w-16 h-16 bg-emerald-100 rounded-full flex items-center justify-center">
              <Upload className="h-8 w-8 text-emerald-600" />
            </div>
            
            <div>
              <h3 className="text-lg font-semibold text-gray-900">
                Sélectionner un fichier CSV
              </h3>
              <p className="text-sm text-gray-500 max-w-md mt-1">
                Supporte les exports de la plupart des banques françaises. 
                Le format sera détecté automatiquement.
              </p>
            </div>

            <Button 
              onClick={handleSelectFile}
              disabled={importing}
              size="lg"
              className="bg-emerald-600 hover:bg-emerald-700"
            >
              {importing ? (
                <>
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                  Import en cours...
                </>
              ) : (
                <>
                  <FileText className="h-4 w-4 mr-2" />
                  Choisir un fichier
                </>
              )}
            </Button>

            <p className="text-xs text-gray-400">
              Formats supportés: CSV (délimiteur auto-détecté)
            </p>
          </div>
        </CardContent>
      </Card>

      {/* Résultat de l'import */}
      {result && (
        <Card className={result.success ? 'border-emerald-200' : 'border-red-200'}>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              {result.success ? (
                <>
                  <CheckCircle className="h-5 w-5 text-emerald-600" />
                  <span className="text-emerald-800">Import réussi</span>
                </>
              ) : (
                <>
                  <AlertCircle className="h-5 w-5 text-red-600" />
                  <span className="text-red-800">Erreur d'import</span>
                </>
              )}
            </CardTitle>
          </CardHeader>
          <CardContent>
            {result.success ? (
              <div className="space-y-4">
                <div className="grid grid-cols-4 gap-4">
                  <div className="bg-gray-50 p-4 rounded-lg text-center">
                    <div className="text-2xl font-bold text-gray-900">
                      {result.total}
                    </div>
                    <div className="text-xs text-gray-500">Total lignes</div>
                  </div>
                  <div className="bg-emerald-50 p-4 rounded-lg text-center">
                    <div className="text-2xl font-bold text-emerald-600">
                      {result.imported}
                    </div>
                    <div className="text-xs text-gray-500">Importées</div>
                  </div>
                  <div className="bg-yellow-50 p-4 rounded-lg text-center">
                    <div className="text-2xl font-bold text-yellow-600">
                      {result.duplicates || 0}
                    </div>
                    <div className="text-xs text-gray-500">Doublons</div>
                  </div>
                  <div className="bg-red-50 p-4 rounded-lg text-center">
                    <div className="text-2xl font-bold text-red-600">
                      {result.errors || 0}
                    </div>
                    <div className="text-xs text-gray-500">Erreurs</div>
                  </div>
                </div>

                {result.fileName && (
                  <p className="text-sm text-gray-600">
                    Fichier: <span className="font-medium">{result.fileName}</span>
                  </p>
                )}

                {result.mappings && (
                  <div className="text-sm text-gray-600">
                    <p className="font-medium mb-1">Colonnes détectées:</p>
                    <div className="flex flex-wrap gap-2">
                      {Object.entries(result.mappings).map(([key, value]) => (
                        value && (
                          <span 
                            key={key}
                            className="bg-gray-100 px-2 py-1 rounded text-xs"
                          >
                            {key}: {value}
                          </span>
                        )
                      ))}
                    </div>
                  </div>
                )}

                {result.errorDetails && result.errorDetails.length > 0 && (
                  <div className="bg-red-50 border border-red-200 rounded-lg p-3">
                    <p className="text-sm font-medium text-red-800 mb-2">
                      Détails des erreurs:
                    </p>
                    <ul className="text-xs text-red-700 space-y-1">
                      {result.errorDetails.slice(0, 5).map((err, i) => (
                        <li key={i}>
                          Ligne {err.row}: {err.error}
                        </li>
                      ))}
                      {result.errorDetails.length > 5 && (
                        <li>... et {result.errorDetails.length - 5} autres erreurs</li>
                      )}
                    </ul>
                  </div>
                )}
              </div>
            ) : (
              <div className="text-red-700">
                <p>{result.error}</p>
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* Historique récent */}
      {recentImports.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Imports récents</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {recentImports.map((imp, index) => (
                <div 
                  key={index}
                  className="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
                >
                  <div className="flex items-center gap-3">
                    <FileText className="h-4 w-4 text-gray-400" />
                    <div>
                      <p className="font-medium text-sm">{imp.fileName}</p>
                      <p className="text-xs text-gray-500">
                        {imp.imported} transactions importées
                      </p>
                    </div>
                  </div>
                  {imp.success ? (
                    <CheckCircle className="h-4 w-4 text-emerald-500" />
                  ) : (
                    <AlertCircle className="h-4 w-4 text-red-500" />
                  )}
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
