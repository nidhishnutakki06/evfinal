import React from 'react';

interface MetricCardProps {
  title: string;
  value: string | number;
  unit?: string;
  icon?: React.ReactNode;
  subtitle?: string;
  statusColor?: 'green' | 'yellow' | 'red' | 'neutral' | 'blue';
  highlight?: boolean;
}

export const MetricCard: React.FC<MetricCardProps> = ({ 
  title, 
  value, 
  unit, 
  icon, 
  subtitle, 
  statusColor = 'neutral',
  highlight = false
}) => {
  const colorMap = {
    green: 'text-green-600 dark:text-green-400',
    yellow: 'text-amber-500 dark:text-amber-400',
    red: 'text-red-600 dark:text-red-400',
    blue: 'text-blue-600 dark:text-blue-400',
    neutral: 'text-black dark:text-white'
  };

  const bgMap = {
    green: 'bg-green-500/10 border-green-500/30',
    yellow: 'bg-amber-500/10 border-amber-500/30',
    red: 'bg-red-500/10 border-red-500/30',
    blue: 'bg-blue-500/10 border-blue-500/30',
    neutral: 'bg-zinc-100 dark:bg-zinc-900 border-zinc-200 dark:border-zinc-800'
  };

  return (
    <div className={`p-3 rounded-lg border flex flex-col justify-between ${highlight ? bgMap[statusColor] : 'bg-zinc-50 dark:bg-zinc-900 border-zinc-200 dark:border-zinc-800'}`}>
      <div className="flex justify-between items-start mb-2">
        <h3 className="text-zinc-500 dark:text-zinc-400 text-[10px] font-bold uppercase tracking-wider">{title}</h3>
        {icon && <div className="text-zinc-400 dark:text-zinc-500">{icon}</div>}
      </div>
      <div className="flex items-baseline space-x-1">
        <span className={`text-xl font-bold ${colorMap[statusColor]}`}>{value}</span>
        {unit && <span className="text-xs text-zinc-500 dark:text-zinc-500 font-semibold">{unit}</span>}
      </div>
      {subtitle && <p className="text-[10px] text-zinc-500 dark:text-zinc-400 mt-1 font-bold">{subtitle}</p>}
    </div>
  );
};
