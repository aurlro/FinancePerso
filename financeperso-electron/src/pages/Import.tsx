import { useState } from 'react';
import { useImport } from '../hooks/useImport';
import { Button } from '../components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Upload, FileText, CheckCircle, AlertCircle, Loader2 } from 'lucide-react';
import { Alert, AlertDescription, AlertTitle } from '../components/ui/alert';

export function Import() {
  const { isImporting, result, error, importFile, reset } = useImport();
  const [delimiter, setDelimiter] = useState(';');

  const handleImport = async () => {
    await importFile({ delimiter });
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-3xl font-bold tracking-tight">Import de transactions</h2>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Upload className="h-5 w-5" />
            Importer un fichier CSV
          </CardTitle>
          <CardDescription>
            Importez vos relevés bancaires au format CSV. Les formats supportés incluent
            les exports des principales banques françaises.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center gap-4">
            <label className="text-sm font-medium">Séparateur :</label>
            <select
              value={delimiter}
              onChange={(e) => setDelimiter(e.target.value)}
              className="border rounded px-2 py-1 text-sm"
              disabled={isImporting}
            >
              <option value=";">Point-virgule (;)</option>
              <option value=",">Virgule (,)</option>
              <option value="\t">Tabulation</option>
            </select>
          </div>

          <Button
            onClick={handleImport}
            disabled={isImporting}
            className="w-full sm:w-auto"
          >
            {isImporting ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Import en cours...
              </>
            ) : (
              <>
                <FileText className="mr-2 h-4 w-4" />
                Sélectionner un fichier CSV
              </>
            )}
          </Button>

          {result && (
            <Alert variant={result.success ? "default" : "destructive"}>
              {result.success ? (
                <CheckCircle className="h-4 w-4" />
              ) : (
                <AlertCircle className="h-4 w-4" />
              )}
              <AlertTitle>
                {result.success ? 'Import réussi' : 'Erreur lors de l\'import'}
              </AlertTitle>
              <AlertDescription>
                {result.success ? (
                  <div className="mt-2 space-y-1">
                    <p>Fichier : <strong>{result.fileName}</strong></p>
                    <p>Total de lignes : {result.total}</p>
                    <p>Importées : <span className="text-green-600 font-medium">{result.imported}</span></p>
                    {result.errors > 0 && (
                      <p>Erreurs : <span className="text-red-600 font-medium">{result.errors}</span></p>
                    )}
                  </div>
                ) : (
                  result.error
                )}
              </AlertDescription>
            </Alert>
          )}

          {error && !result && (
            <Alert variant="destructive">
              <AlertCircle className="h-4 w-4" />
              <AlertTitle>Erreur</AlertTitle>
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Formats supportés</CardTitle>
          <CardDescription>
            Les colonnes suivantes sont automatiquement détectées :
          </CardDescription>
        </CardHeader>
        <CardContent>
          <ul className="list-disc list-inside space-y-1 text-sm text-muted-foreground">
            <li><strong>Date</strong> : Date de la transaction (JJ/MM/AAAA, AAAA-MM-JJ...)</li>
            <li><strong>Description</strong> : Libellé de la transaction</li>
            <li><strong>Montant</strong> : Montant en euros (positif = revenu, négatif = dépense)</li>
            <li><strong>Catégorie</strong> : Catégorie optionnelle (sinon "Non catégorisé")</li>
          </ul>
          <p className="mt-4 text-sm text-muted-foreground">
            Les doublons (même date, description et montant) sont automatiquement ignorés.
          </p>
        </CardContent>
      </Card>
    </div>
  );
}
