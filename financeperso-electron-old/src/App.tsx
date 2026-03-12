import { useEffect, useState } from 'react'
import { Button } from './components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from './components/ui/card'

function App() {
  const [version, setVersion] = useState<string>('loading...')
  const [ping, setPing] = useState<string>('')

  useEffect(() => {
    // Test IPC communication
    const testIPC = async () => {
      try {
        if (window.electronAPI) {
          const v = await window.electronAPI.getVersion()
          setVersion(v)
          const p = window.electronAPI.ping()
          setPing(p)
        } else {
          setVersion('not available')
          setPing('not available')
        }
      } catch (e) {
        setVersion('error: ' + (e as Error).message)
      }
    }
    testIPC()
  }, [])

  return (
    <div className="min-h-screen bg-gradient-to-br from-emerald-50 to-teal-50 p-8">
      <div className="max-w-4xl mx-auto space-y-6">
        <h1 className="text-4xl font-bold text-emerald-800">
          🌿 FinancePerso
        </h1>
        <p className="text-emerald-600">
          Gestion financière de couple - Phase 0
        </p>

        <Card>
          <CardHeader>
            <CardTitle>Electron IPC Test</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <p className="text-sm text-muted-foreground">
                Electron Version: <span className="font-mono">{version}</span>
              </p>
              <p className="text-sm text-muted-foreground">
                Ping Test: <span className="font-mono">{ping}</span>
              </p>
              <p className="text-sm text-muted-foreground">
                Platform: <span className="font-mono">{window.electronAPI?.platform || 'web'}</span>
              </p>
            </div>
            
            <div className="flex gap-2">
              <Button 
                onClick={() => alert('Button clicked!')}
                className="bg-emerald-600 hover:bg-emerald-700"
              >
                Test Button
              </Button>
              <Button 
                variant="outline"
                onClick={async () => {
                  if (window.electronAPI) {
                    const v = await window.electronAPI.getVersion()
                    alert('Version: ' + v)
                  }
                }}
              >
                Get Version
              </Button>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Configuration</CardTitle>
          </CardHeader>
          <CardContent>
            <ul className="space-y-2 text-sm">
              <li>✅ Electron Main Process (.cjs)</li>
              <li>✅ Preload Script (.cjs)</li>
              <li>✅ React + TypeScript + Vite</li>
              <li>✅ Tailwind CSS + shadcn/ui</li>
              <li>🔄 SQLite Integration (next)</li>
              <li>🔄 Services Layer (next)</li>
            </ul>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}

export default App
