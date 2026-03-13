import * as React from "react"
import { cn } from "@/lib/utils"
import { Skeleton } from "./skeleton"
import { Card, CardContent, CardHeader } from "./card"

// Generic loading state wrapper
export interface LoadingStateProps {
  children: React.ReactNode
  className?: string
}

export function LoadingState({ children, className }: LoadingStateProps) {
  return (
    <div className={cn("animate-pulse space-y-4", className)}>
      {children}
    </div>
  )
}

// Dashboard loading skeleton
export function DashboardLoading() {
  return (
    <div className="space-y-6">
      {/* KPI Cards Loading */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {Array.from({ length: 4 }).map((_, i) => (
          <Card key={i}>
            <CardHeader className="pb-2">
              <Skeleton className="h-4 w-24" />
            </CardHeader>
            <CardContent>
              <Skeleton className="h-8 w-32 mb-2" />
              <Skeleton className="h-3 w-16" />
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Charts Loading */}
      <div className="grid gap-4 md:grid-cols-2">
        <Card>
          <CardHeader>
            <Skeleton className="h-5 w-40" />
          </CardHeader>
          <CardContent>
            <Skeleton variant="card" className="h-64 w-full" />
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <Skeleton className="h-5 w-40" />
          </CardHeader>
          <CardContent>
            <Skeleton variant="card" className="h-64 w-full" />
          </CardContent>
        </Card>
      </div>
    </div>
  )
}

// Transactions loading skeleton
export function TransactionsLoading() {
  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <Skeleton className="h-8 w-48" />
        <Skeleton className="h-10 w-32" />
      </div>

      {/* Filter bar */}
      <div className="flex gap-2">
        <Skeleton className="h-10 w-40" />
        <Skeleton className="h-10 w-40" />
        <Skeleton className="h-10 w-32" />
      </div>

      {/* Transaction list */}
      <Card>
        <CardContent className="p-0">
          {Array.from({ length: 8 }).map((_, i) => (
            <div
              key={i}
              className="flex items-center justify-between border-b p-4 last:border-0"
            >
              <div className="flex items-center gap-3">
                <Skeleton variant="circle" className="h-10 w-10" />
                <div className="space-y-2">
                  <Skeleton className="h-4 w-32" />
                  <Skeleton className="h-3 w-24" />
                </div>
              </div>
              <div className="text-right">
                <Skeleton className="h-4 w-20" />
                <Skeleton className="h-3 w-16 mt-1" />
              </div>
            </div>
          ))}
        </CardContent>
      </Card>
    </div>
  )
}

// Budgets loading skeleton
export function BudgetsLoading() {
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <Skeleton className="h-8 w-32" />
        <Skeleton className="h-10 w-32" />
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {Array.from({ length: 6 }).map((_, i) => (
          <Card key={i}>
            <CardContent className="p-4">
              <div className="flex items-center justify-between mb-4">
                <Skeleton variant="circle" className="h-10 w-10" />
                <Skeleton className="h-5 w-20" />
              </div>
              <Skeleton className="h-6 w-32 mb-2" />
              <Skeleton className="h-2.5 w-full mb-2" />
              <div className="flex justify-between">
                <Skeleton className="h-3 w-20" />
                <Skeleton className="h-3 w-20" />
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  )
}

// Import loading skeleton
export function ImportLoading() {
  return (
    <div className="space-y-4">
      <Skeleton className="h-8 w-48" />
      
      <Card>
        <CardContent className="p-8">
          <div className="flex flex-col items-center justify-center text-center">
            <Skeleton variant="circle" className="h-16 w-16 mb-4" />
            <Skeleton className="h-6 w-48 mb-2" />
            <Skeleton className="h-4 w-64" />
          </div>
        </CardContent>
      </Card>

      {/* Preview table loading */}
      <Card>
        <CardHeader>
          <Skeleton className="h-5 w-40" />
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {Array.from({ length: 5 }).map((_, i) => (
              <div key={i} className="flex gap-4">
                <Skeleton className="h-8 flex-1" />
                <Skeleton className="h-8 flex-1" />
                <Skeleton className="h-8 flex-1" />
                <Skeleton className="h-8 w-20" />
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

// Generic table loading
export function TableLoading({ rows = 5 }: { rows?: number }) {
  return (
    <div className="space-y-3">
      <div className="flex gap-4">
        <Skeleton className="h-8 flex-1" />
        <Skeleton className="h-8 flex-1" />
        <Skeleton className="h-8 flex-1" />
        <Skeleton className="h-8 w-24" />
      </div>
      {Array.from({ length: rows }).map((_, i) => (
        <div key={i} className="flex gap-4">
          <Skeleton className="h-12 flex-1" />
          <Skeleton className="h-12 flex-1" />
          <Skeleton className="h-12 flex-1" />
          <Skeleton className="h-12 w-24" />
        </div>
      ))}
    </div>
  )
}
