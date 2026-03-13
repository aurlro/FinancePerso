import * as React from "react"
import { cn } from "@/lib/utils"
import { Card, CardContent, CardHeader } from "./ui/card"
import { TrendingUp, TrendingDown, Minus, LucideIcon } from "lucide-react"

export interface KPICardProps {
  title: string
  value: string | number
  icon: LucideIcon | string
  trend?: {
    value: number
    label?: string
    direction?: "up" | "down" | "neutral"
  }
  color?: "emerald" | "blue" | "amber" | "red" | "purple"
  className?: string
}

const colorConfig = {
  emerald: {
    bg: "bg-emerald-50",
    text: "text-emerald-600",
    border: "border-emerald-200",
    iconBg: "bg-emerald-100",
  },
  blue: {
    bg: "bg-blue-50",
    text: "text-blue-600",
    border: "border-blue-200",
    iconBg: "bg-blue-100",
  },
  amber: {
    bg: "bg-amber-50",
    text: "text-amber-600",
    border: "border-amber-200",
    iconBg: "bg-amber-100",
  },
  red: {
    bg: "bg-red-50",
    text: "text-red-600",
    border: "border-red-200",
    iconBg: "bg-red-100",
  },
  purple: {
    bg: "bg-purple-50",
    text: "text-purple-600",
    border: "border-purple-200",
    iconBg: "bg-purple-100",
  },
}

export function KPICard({
  title,
  value,
  icon: Icon,
  trend,
  color = "emerald",
  className,
}: KPICardProps) {
  const colors = colorConfig[color]
  
  // Determine trend direction if not specified
  const trendDirection = trend?.direction ?? 
    (trend ? (trend.value > 0 ? "up" : trend.value < 0 ? "down" : "neutral") : "neutral")
  
  const TrendIcon = trendDirection === "up" 
    ? TrendingUp 
    : trendDirection === "down" 
    ? TrendingDown 
    : Minus

  const trendColorClass = trendDirection === "up"
    ? "text-emerald-600"
    : trendDirection === "down"
    ? "text-red-600"
    : "text-gray-400"

  const displayTrendValue = trend ? Math.abs(trend.value) : 0

  return (
    <Card className={cn(colors.border, "border", className)}>
      <CardHeader className="pb-2 flex flex-row items-center justify-between">
        <span className="text-sm font-medium text-muted-foreground">
          {title}
        </span>
        <div className={cn("p-2 rounded-lg", colors.iconBg)}>
          {typeof Icon === "string" ? (
            <span className="text-lg">{Icon}</span>
          ) : (
            <Icon className={cn("h-5 w-5", colors.text)} />
          )}
        </div>
      </CardHeader>
      <CardContent>
        <div className="flex items-baseline gap-2">
          <p className={cn("text-2xl font-bold", colors.text)}>
            {value}
          </p>
        </div>
        {trend && (
          <div className="flex items-center gap-1 mt-2 text-sm">
            <TrendIcon className={cn("h-4 w-4", trendColorClass)} />
            <span className={trendColorClass}>
              {trend.value > 0 ? "+" : "-"}{displayTrendValue.toFixed(1)}%
            </span>
            {trend.label && (
              <span className="text-muted-foreground ml-1">{trend.label}</span>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  )
}

// KPI Grid for multiple cards
export interface KPICardGridProps {
  children: React.ReactNode
  className?: string
  columns?: 2 | 3 | 4
}

export function KPICardGrid({
  children,
  className,
  columns = 4,
}: KPICardGridProps) {
  const gridCols = {
    2: "md:grid-cols-2",
    3: "md:grid-cols-3",
    4: "md:grid-cols-2 lg:grid-cols-4",
  }

  return (
    <div className={cn("grid gap-4", gridCols[columns], className)}>
      {children}
    </div>
  )
}
