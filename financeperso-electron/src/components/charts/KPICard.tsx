import * as React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { TrendingUp, TrendingDown, Minus, Wallet, ArrowDownLeft, ArrowUpRight } from 'lucide-react';

interface KPICardProps {
  title: string;
  value: number;
  variant: 'income' | 'expense' | 'balance';
  trend?: number;
  trendLabel?: string;
}

const variantConfig = {
  income: {
    icon: ArrowDownLeft,
    colorClass: 'text-green-500',
    bgClass: 'bg-green-50',
    borderClass: 'border-green-200',
    prefix: '+',
  },
  expense: {
    icon: ArrowUpRight,
    colorClass: 'text-red-500',
    bgClass: 'bg-red-50',
    borderClass: 'border-red-200',
    prefix: '-',
  },
  balance: {
    icon: Wallet,
    colorClass: 'text-emerald-500',
    bgClass: 'bg-emerald-50',
    borderClass: 'border-emerald-200',
    prefix: '',
  },
};

export function KPICard({ title, value, variant, trend, trendLabel }: KPICardProps) {
  const config = variantConfig[variant];
  const Icon = config.icon;
  
  const isPositiveTrend = trend !== undefined && trend >= 0;
  const TrendIcon = trend === undefined ? Minus : isPositiveTrend ? TrendingUp : TrendingDown;
  const trendColorClass = trend === undefined 
    ? 'text-gray-400' 
    : isPositiveTrend 
      ? variant === 'expense' ? 'text-red-500' : 'text-green-500'
      : variant === 'expense' ? 'text-green-500' : 'text-red-500';

  const displayValue = value >= 0 ? value : Math.abs(value);
  const prefix = value >= 0 ? config.prefix : '-';

  return (
    <Card className={`${config.borderClass} border`}>
      <CardHeader className="pb-2 flex flex-row items-center justify-between">
        <CardTitle className="text-sm font-medium text-muted-foreground">
          {title}
        </CardTitle>
        <div className={`p-2 rounded-lg ${config.bgClass}`}>
          <Icon className={`h-4 w-4 ${config.colorClass}`} />
        </div>
      </CardHeader>
      <CardContent>
        <div className="flex items-baseline gap-2">
          <p className={`text-3xl font-bold ${config.colorClass}`}>
            {prefix}{displayValue.toFixed(2)}€
          </p>
        </div>
        {trend !== undefined && (
          <div className="flex items-center gap-1 mt-2 text-sm">
            <TrendIcon className={`h-4 w-4 ${trendColorClass}`} />
            <span className={trendColorClass}>
              {isPositiveTrend ? '+' : ''}{trend.toFixed(1)}%
            </span>
            {trendLabel && (
              <span className="text-muted-foreground ml-1">{trendLabel}</span>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
