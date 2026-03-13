import * as React from "react"
import { cn } from "@/lib/utils"
import { Button } from "./button"
import { AlertCircle, RefreshCw } from "lucide-react"

export interface ErrorStateProps {
  error?: Error | string | null
  title?: string
  description?: string
  onRetry?: () => void
  className?: string
}

export function ErrorState({
  error,
  title = "Une erreur s'est produite",
  description,
  onRetry,
  className,
}: ErrorStateProps) {
  const errorMessage = error instanceof Error 
    ? error.message 
    : error || description || "Veuillez réessayer plus tard."

  return (
    <div
      className={cn(
        "flex flex-col items-center justify-center rounded-lg border border-red-200 bg-red-50 p-8 text-center",
        className
      )}
    >
      <div className="mb-4 rounded-full bg-red-100 p-3">
        <AlertCircle className="h-6 w-6 text-red-600" />
      </div>
      <h3 className="mb-2 text-lg font-semibold text-red-900">{title}</h3>
      <p className="mb-4 max-w-sm text-sm text-red-700">{errorMessage}</p>
      {onRetry && (
        <Button
          onClick={onRetry}
          variant="outline"
          className="border-red-300 text-red-700 hover:bg-red-100"
        >
          <RefreshCw className="mr-2 h-4 w-4" />
          Réessayer
        </Button>
      )}
    </div>
  )
}

// Error Boundary Component
interface ErrorBoundaryProps {
  children: React.ReactNode
  fallback?: React.ReactNode
}

interface ErrorBoundaryState {
  hasError: boolean
  error: Error | null
}

export class ErrorBoundary extends React.Component<
  ErrorBoundaryProps,
  ErrorBoundaryState
> {
  constructor(props: ErrorBoundaryProps) {
    super(props)
    this.state = { hasError: false, error: null }
  }

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return { hasError: true, error }
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error("ErrorBoundary caught an error:", error, errorInfo)
  }

  handleRetry = () => {
    this.setState({ hasError: false, error: null })
    window.location.reload()
  }

  render() {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback
      }
      return (
        <div className="flex min-h-screen items-center justify-center p-4">
          <ErrorState
            error={this.state.error}
            title="Oups ! Quelque chose s'est mal passé"
            onRetry={this.handleRetry}
            className="w-full max-w-md"
          />
        </div>
      )
    }

    return this.props.children
  }
}
